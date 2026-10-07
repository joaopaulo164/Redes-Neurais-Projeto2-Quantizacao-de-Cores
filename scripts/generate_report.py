from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));from src.experiments.runner import aggregate
s=aggregate();cols=[c for c in s.columns if c in ['image_name','model','capacity_requested','quantization_error_mean','quantization_error_std','topographic_error_mean','topographic_error_std','mean_delta_e_mean','mean_delta_e_std','training_time_s_mean','inference_time_s_mean']];table=s[cols].round(4).to_markdown(index=False)
text='# Relatório Final - Projeto 2: Quantização de Cores\n\n## 1. Introdução\n\n## 2. Fundamentação teórica\n\n## 3. Metodologia\n\n## 4. Resultados quantitativos\n\n'+table+'\n\n## 5. Resultados qualitativos\n\nInserir figuras de `outputs/figures/`.\n\n## 6. Discussão\n\nResponder às quatro questões da proposta.\n\n## 7. Limitações\n\n## 8. Conclusão\n';Path('report/relatorio_gerado.md').write_text(text,encoding='utf-8')
