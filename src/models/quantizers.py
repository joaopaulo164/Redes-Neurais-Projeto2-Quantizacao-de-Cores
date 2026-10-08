"""PyTorch implementations of neural color quantizers."""

import math
from os import PathLike
from typing import Any

import torch


class Base:
    """Shared interface and operations for color quantizers.

    Concrete quantizers provide prototype assignment, learned prototypes, and
    a serializable state. :class:`SOM`, :class:`TorchKMeans`, and :class:`GNG`
    inherit this class to share image reconstruction and checkpoint saving.
    """

    def quantize(
        self,
        image_data: torch.Tensor,
        batch_size: int = 65536,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Replace each input color with its nearest learned prototype.

        Args:
            image_data: Tensor of RGB pixels to quantize.
            batch_size: Maximum number of pixels assigned at once.

        Returns:
            A tuple containing reconstructed pixels and their prototype
            indices.
        """
        bmu_indices = self.predict_bmu(image_data, batch_size)
        return self.prototypes()[bmu_indices], bmu_indices

    def save(self, path: str | PathLike[str]) -> None:
        """Save this quantizer's state dictionary to a file.

        Args:
            path: Destination path for the PyTorch checkpoint.
        """
        torch.save(self.state_dict(), path)


class SOM(Base):
    """Self-Organizing Map color quantizer.

    The SOM extends :class:`Base` with a fixed two-dimensional prototype grid.
    During fitting, each input color updates its Best Matching Unit (BMU) and
    nearby grid prototypes according to a decaying neighborhood function.

    Args:
        rows: Number of grid rows.
        cols: Number of grid columns.
        epochs: Number of passes over the training pixels.
        batch_size: Number of pixels processed per training update.
        lr0: Initial learning rate.
        lrf: Final learning rate.
        sigma_final: Final neighborhood radius.
        device: PyTorch device used for tensors and training.
        seed: Seed used to initialize the random generator.
    """

    def __init__(
        self,
        rows: int,
        cols: int,
        epochs: int = 15,
        batch_size: int = 512,
        lr0: float = 0.5,
        lrf: float = 0.05,
        sigma_final: float = 0.5,
        device: str = "cpu",
        seed: int = 13,
    ) -> None:
        self.rows = rows
        self.cols = cols
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr0 = lr0
        self.lrf = lrf
        self.s0 = max(rows, cols) / 2
        self.sf = sigma_final
        self.device = device
        self.seed = seed
        self.history: list[dict[str, int | float]] = []

        row_indices, column_indices = torch.meshgrid(
            torch.arange(rows),
            torch.arange(cols),
            indexing="ij",
        )
        self.grid = (
            torch.stack(
                [row_indices.flatten(), column_indices.flatten()],
                1,
            )
            .float()
            .to(device)
        )

    def fit(self, image_data: torch.Tensor) -> "SOM":
        """Train the map by moving grid prototypes toward sampled colors.

        Args:
            image_data: Training RGB pixels with values in the range [0, 1].

        Returns:
            This fitted SOM instance.
        """
        image_data = image_data.to(self.device)
        generator = torch.Generator(device=self.device).manual_seed(self.seed)
        prototype_count = self.rows * self.cols

        if len(image_data) >= prototype_count:
            random_order = torch.randperm(
                len(image_data),
                generator=generator,
                device=self.device,
            )
            self.weights = image_data[random_order[:prototype_count]].clone()
        else:
            self.weights = torch.rand(
                prototype_count,
                3,
                generator=generator,
                device=self.device,
            )

        total_steps = max(
            1,
            self.epochs * math.ceil(len(image_data) / self.batch_size) - 1,
        )
        step = 0

        for epoch_index in range(self.epochs):
            random_order = torch.randperm(
                len(image_data),
                generator=generator,
                device=self.device,
            )
            quantization_error = 0.0

            for batch_start in range(0, len(image_data), self.batch_size):
                batch_indices = random_order[
                    batch_start : batch_start + self.batch_size
                ]
                batch_data = image_data[batch_indices]
                progress = step / total_steps

                # Geometric interpolation decays both learning rate and radius.
                learning_rate = self.lr0 * (self.lrf / self.lr0) ** progress
                sigma = self.s0 * (self.sf / self.s0) ** progress

                # cdist gives each pixel-to-prototype distance; argmin selects
                # the closest prototype, the Best Matching Unit (BMU).
                distances = torch.cdist(batch_data, self.weights)
                bmu_indices = distances.argmin(1)
                quantization_error += (
                    distances.gather(
                        1,
                        bmu_indices[:, None],
                    )
                    .sum()
                    .item()
                )

                # Squared grid distance defines a Gaussian neighborhood around
                # each BMU; weighted means move nearby prototypes toward
                # colors.
                grid_distances = (
                    (self.grid[None] - self.grid[bmu_indices][:, None]) ** 2
                ).sum(2)
                neighborhood_weights = torch.exp(
                    -grid_distances / (2 * sigma * sigma)
                )
                weight_sums = neighborhood_weights.sum(0)[:, None].clamp_min(
                    1e-12
                )
                neighborhood_means = (
                    neighborhood_weights.T @ batch_data
                ) / weight_sums
                self.weights += learning_rate * (
                    neighborhood_means - self.weights
                )
                self.weights.clamp_(0, 1)
                step += 1

            self.history.append(
                {
                    "epoch": epoch_index + 1,
                    "qe": quantization_error / len(image_data),
                    "lr": learning_rate,
                    "sigma": sigma,
                }
            )

        return self

    def predict_bmu(
        self,
        image_data: torch.Tensor,
        batch_size: int = 65536,
    ) -> torch.Tensor:
        """Return the closest SOM prototype index for each input color.

        Args:
            image_data: RGB pixels to assign to prototypes.
            batch_size: Maximum number of pixels processed per distance call.

        Returns:
            A one-dimensional tensor containing BMU indices.
        """
        return torch.cat(
            [
                torch.cdist(
                    image_data[batch_start : batch_start + batch_size].to(
                        self.device
                    ),
                    self.weights,
                ).argmin(1)
                for batch_start in range(0, len(image_data), batch_size)
            ]
        )

    def two_best(
        self,
        image_data: torch.Tensor,
        batch_size: int = 65536,
    ) -> torch.Tensor:
        """Return the two closest SOM prototype indices per input color.

        Args:
            image_data: RGB pixels to assign to prototypes.
            batch_size: Maximum number of pixels processed per distance call.

        Returns:
            A tensor with the indices of the two nearest prototypes per pixel.
        """
        return torch.cat(
            [
                torch.cdist(
                    image_data[batch_start : batch_start + batch_size].to(
                        self.device
                    ),
                    self.weights,
                )
                .topk(2, largest=False)
                .indices
                for batch_start in range(0, len(image_data), batch_size)
            ]
        )

    def prototypes(self) -> torch.Tensor:
        """Return the learned SOM prototype colors.

        Returns:
            A tensor containing one RGB prototype per grid node.
        """
        return self.weights

    def state_dict(self) -> dict[str, Any]:
        """Return the model name, topology, weights, and training history.

        Returns:
            A dictionary suitable for checkpoint serialization.
        """
        return {
            "model": "som",
            "rows": self.rows,
            "cols": self.cols,
            "weights": self.weights.cpu(),
            "history": self.history,
        }


class TorchKMeans(Base):
    """K-means color quantizer implemented with PyTorch tensors.

    This :class:`Base` implementation initializes centroids with the
    k-means++ distance-weighted strategy and repeatedly replaces each
    non-empty cluster centroid with its assigned pixels' mean.

    Args:
        k: Number of requested color centroids.
        max_iter: Maximum number of centroid-update iterations.
        tolerance: Stop when the overall centroid shift falls below this value.
        device: PyTorch device used for tensors and training.
        seed: Seed used to initialize the random generator.
    """

    def __init__(
        self,
        k: int,
        max_iter: int = 100,
        tolerance: float = 1e-4,
        device: str = "cpu",
        seed: int = 13,
    ) -> None:
        self.k = k
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.device = device
        self.seed = seed
        self.history: list[dict[str, int | float]] = []

    def fit(self, image_data: torch.Tensor) -> "TorchKMeans":
        """Fit centroids using k-means++ initialization and Lloyd updates.

        Args:
            image_data: Training RGB pixels with values in the range [0, 1].

        Returns:
            This fitted TorchKMeans instance.
        """
        image_data = image_data.to(self.device)
        generator = torch.Generator(device=self.device).manual_seed(self.seed)
        first_index = torch.randint(
            len(image_data),
            (1,),
            generator=generator,
            device=self.device,
        )
        centers = [image_data[first_index].squeeze()]

        # k-means++ samples each next center in proportion to squared distance
        # from the closest existing center; zero total distance uses a random
        # pick.
        for _ in range(1, self.k):
            squared_distances = (
                torch.cdist(image_data, torch.stack(centers))
                .pow(2)
                .min(1)
                .values
            )
            if squared_distances.sum() > 0:
                next_index = torch.multinomial(
                    squared_distances / squared_distances.sum(),
                    1,
                    generator=generator,
                )
            else:
                next_index = torch.randint(
                    len(image_data),
                    (1,),
                    generator=generator,
                    device=self.device,
                )
            centers.append(image_data[next_index].squeeze())

        self.centroids = torch.stack(centers)

        for iteration_index in range(self.max_iter):
            distances = torch.cdist(image_data, self.centroids)
            labels = distances.argmin(1)
            new_centroids = self.centroids.clone()

            # Each centroid becomes its cluster's arithmetic mean; retaining
            # the prior value for an empty cluster matches the original logic.
            for centroid_index in range(self.k):
                assigned_pixels = labels == centroid_index
                if assigned_pixels.any():
                    new_centroids[centroid_index] = image_data[
                        assigned_pixels
                    ].mean(0)

            centroid_shift = torch.norm(new_centroids - self.centroids).item()
            self.centroids = new_centroids
            self.history.append(
                {
                    "iteration": iteration_index + 1,
                    "shift": centroid_shift,
                }
            )
            if centroid_shift < self.tolerance:
                break

        return self

    def predict_bmu(
        self,
        image_data: torch.Tensor,
        batch_size: int = 65536,
    ) -> torch.Tensor:
        """Assign each input color to its nearest centroid.

        Args:
            image_data: RGB pixels to assign to centroids.
            batch_size: Maximum number of pixels processed per distance call.

        Returns:
            A one-dimensional tensor containing centroid indices.
        """
        return torch.cat(
            [
                torch.cdist(
                    image_data[batch_start : batch_start + batch_size].to(
                        self.device
                    ),
                    self.centroids,
                ).argmin(1)
                for batch_start in range(0, len(image_data), batch_size)
            ]
        )

    def prototypes(self) -> torch.Tensor:
        """Return the learned color centroids.

        Returns:
            A tensor containing the k RGB centroids.
        """
        return self.centroids

    def state_dict(self) -> dict[str, Any]:
        """Return centroids and training history for checkpointing.

        Returns:
            A dictionary suitable for checkpoint serialization.
        """
        return {
            "model": "kmeans",
            "centroids": self.centroids.cpu(),
            "history": self.history,
        }


class GNG(Base):
    """Growing Neural Gas color quantizer with a dynamic prototype graph.

    GNG extends :class:`Base` with nodes (color prototypes) and undirected,
    age-tracked edges. It adapts the nearest nodes to each sampled color and
    periodically inserts a node between high-error neighboring nodes.

    Args:
        max_nodes: Maximum number of nodes in the graph.
        steps: Number of sampled-pixel updates.
        eps_b: Learning rate for the winning node.
        eps_n: Learning rate for neighboring nodes.
        insertion_interval: Number of updates between node insertion attempts.
        max_edge_age: Maximum edge age before an edge is removed.
        alpha: Error reduction applied when inserting a node.
        beta: Per-step decay applied to all accumulated errors.
        device: PyTorch device used for tensors and training.
        seed: Seed used to initialize the random generator.
    """

    def __init__(
        self,
        max_nodes: int,
        steps: int = 100000,
        eps_b: float = 0.05,
        eps_n: float = 0.0006,
        insertion_interval: int = 100,
        max_edge_age: int = 90,
        alpha: float = 0.5,
        beta: float = 0.005,
        device: str = "cpu",
        seed: int = 13,
    ) -> None:
        self.max_nodes = max_nodes
        self.steps = steps
        self.eb = eps_b
        self.en = eps_n
        self.lam = insertion_interval
        self.amax = max_edge_age
        self.alpha = alpha
        self.beta = beta
        self.device = device
        self.seed = seed
        self.edges: dict[tuple[int, int], int] = {}
        self.history: list[dict[str, int]] = []

    def edge(self, first_node: int, second_node: int) -> tuple[int, int]:
        """Return a canonical key for an undirected edge.

        Args:
            first_node: Index of one endpoint.
            second_node: Index of the other endpoint.

        Returns:
            An endpoint tuple ordered from the smaller index to the larger.
        """
        return min(int(first_node), int(second_node)), max(
            int(first_node),
            int(second_node),
        )

    def neighbors(self, node_index: int) -> list[int]:
        """Return all graph nodes connected to the given node.

        Args:
            node_index: Node whose adjacent nodes are requested.

        Returns:
            A list of neighboring node indices.
        """
        return [
            second_node if first_node == node_index else first_node
            for first_node, second_node in self.edges
            if first_node == node_index or second_node == node_index
        ]

    def insert(self) -> None:
        """Insert a node between the highest-error node and its best neighbor.

        Insertion is skipped when the graph has reached its node capacity, has
        no edges, or the selected high-error node has no neighbors.
        """
        if len(self.weights) >= self.max_nodes or not self.edges:
            return

        highest_error_node = int(self.errors.argmax())
        neighboring_nodes = self.neighbors(highest_error_node)
        if not neighboring_nodes:
            return

        highest_error_neighbor = max(
            neighboring_nodes,
            key=lambda node_index: float(self.errors[node_index]),
        )
        inserted_node = len(self.weights)
        inserted_weight = (
            self.weights[highest_error_node]
            + self.weights[highest_error_neighbor]
        ) / 2
        self.weights = torch.cat([self.weights, inserted_weight[None]])

        self.errors[highest_error_node] *= self.alpha
        self.errors[highest_error_neighbor] *= self.alpha
        inserted_error = (
            self.errors[highest_error_node]
            + self.errors[highest_error_neighbor]
        ) / 2
        self.errors = torch.cat([self.errors, inserted_error[None]])

        # Replace the old endpoint edge with two edges through the new node.
        self.edges.pop(
            self.edge(highest_error_node, highest_error_neighbor),
            None,
        )
        self.edges[self.edge(highest_error_node, inserted_node)] = 0
        self.edges[self.edge(highest_error_neighbor, inserted_node)] = 0

    def fit(self, image_data: torch.Tensor) -> "GNG":
        """Train the graph by adapting nodes and periodically inserting nodes.

        Args:
            image_data: Training RGB pixels with values in the range [0, 1].

        Returns:
            This fitted GNG instance.
        """
        image_data = image_data.to(self.device)
        generator = torch.Generator(device=self.device).manual_seed(self.seed)
        initial_indices = torch.randperm(
            len(image_data),
            generator=generator,
            device=self.device,
        )[:2]
        self.weights = image_data[initial_indices].clone()
        self.errors = torch.zeros(2, device=self.device)

        for step in range(1, self.steps + 1):
            sample_index = torch.randint(
                len(image_data),
                (1,),
                generator=generator,
                device=self.device,
            )
            sample = image_data[sample_index].squeeze()

            # Squared Euclidean distances identify the first and second BMUs.
            squared_distances = ((self.weights - sample) ** 2).sum(1)
            best_nodes = squared_distances.topk(2, largest=False).indices
            winner_node, second_node = int(best_nodes[0]), int(best_nodes[1])
            self.errors[winner_node] += squared_distances[winner_node]

            # Age edges incident to the winner before refreshing its BMU edge.
            for edge_key in list(self.edges):
                if winner_node in edge_key:
                    self.edges[edge_key] += 1

            self.weights[winner_node] += self.eb * (
                sample - self.weights[winner_node]
            )
            neighboring_nodes = self.neighbors(winner_node)
            if neighboring_nodes:
                neighbor_indices = torch.tensor(
                    neighboring_nodes,
                    device=self.device,
                )
                self.weights[neighbor_indices] += self.en * (
                    sample - self.weights[neighbor_indices]
                )

            # Refresh or create the BMU edge at age zero, then discard stale
            # edges.
            self.edges[self.edge(winner_node, second_node)] = 0
            self.edges = {
                edge_key: age
                for edge_key, age in self.edges.items()
                if age <= self.amax
            }

            if step % self.lam == 0:
                self.insert()
            self.errors *= 1 - self.beta

            if step % max(1, self.steps // 100) == 0:
                self.history.append(
                    {
                        "step": step,
                        "nodes": len(self.weights),
                        "edges": len(self.edges),
                    }
                )

        return self

    def predict_bmu(
        self,
        image_data: torch.Tensor,
        batch_size: int = 65536,
    ) -> torch.Tensor:
        """Assign each input color to its nearest GNG node.

        Args:
            image_data: RGB pixels to assign to graph nodes.
            batch_size: Maximum number of pixels processed per distance call.

        Returns:
            A one-dimensional tensor containing node indices.
        """
        return torch.cat(
            [
                torch.cdist(
                    image_data[batch_start : batch_start + batch_size].to(
                        self.device
                    ),
                    self.weights,
                ).argmin(1)
                for batch_start in range(0, len(image_data), batch_size)
            ]
        )

    def two_best(
        self,
        image_data: torch.Tensor,
        batch_size: int = 65536,
    ) -> torch.Tensor:
        """Return the two closest GNG node indices per input color.

        Args:
            image_data: RGB pixels to assign to graph nodes.
            batch_size: Maximum number of pixels processed per distance call.

        Returns:
            A tensor with the indices of the two nearest nodes per pixel.
        """
        return torch.cat(
            [
                torch.cdist(
                    image_data[batch_start : batch_start + batch_size].to(
                        self.device
                    ),
                    self.weights,
                )
                .topk(2, largest=False)
                .indices
                for batch_start in range(0, len(image_data), batch_size)
            ]
        )

    def prototypes(self) -> torch.Tensor:
        """Return the learned GNG node colors.

        Returns:
            A tensor containing one RGB prototype per graph node.
        """
        return self.weights

    def state_dict(self) -> dict[str, Any]:
        """Return node weights, accumulated errors, graph edges, and history.

        Returns:
            A dictionary suitable for checkpoint serialization.
        """
        return {
            "model": "gng",
            "weights": self.weights.cpu(),
            "errors": self.errors.cpu(),
            "edges": self.edges,
            "history": self.history,
        }
