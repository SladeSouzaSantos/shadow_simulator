# ☀️ Shadow Sim Pro

**Shadow Sim Pro** é uma ferramenta técnica de análise solar desenvolvida para prever o impacto de sombreamento em projetos de engenharia e urbanismo. Através de cálculos astronômicos, o simulador determina o azimute e a altitude solar para gerar projeções de sombras em tempo real.

## 🚀 Funcionalidades
- **Cálculo Geográfico**: Baseado em latitude e data (dia do ano).
- **Trajetória Solar**: Visualização do rastro do sol no céu (sistema polar).
- **Relatório de Sombras**: Tabela horária com filtragem de valores astronômicos (limite de 1000x a altura).
- **Bússola de Engenharia**: Orientação intuitiva com Norte no topo (0°).
- **Interface Interativa**: Desenvolvido com Streamlit e Plotly.

## 🛠️ Stack Tecnológica
- **Linguagem**: Python 3.10
- **Dashboard**: Streamlit
- **Gráficos**: Plotly (Polar charts)
- **Containerização**: Docker & Docker Swarm
- **CI/CD**: GitHub Actions (Build ARM64 para Raspberry Pi)
- **Rede**: Tailscale (Acesso remoto seguro)

## 📦 Como Executar (Localmente)
1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o app:

```bash
streamlit run shadow_app.py
```
## 🏗️ Deploy no Raspberry Pi
O deploy é automatizado via GitHub Actions. A cada push na branch main:

- **O código passa por um Lint de validação. 

- **Uma imagem Docker ARM64 é gerada e enviada ao GHCR. 

- **O deploy é realizado via SSH no Raspberry Pi através da rede Tailscale. 

- **O serviço é exposto via Nginx na porta 8090.

Desenvolvido por Phasscode - 2026.