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
## 🏗️ Fluxo de Deploy Automatizado

O deploy deste projeto é 100% automatizado via **GitHub Actions**, garantindo que a versão em produção no Raspberry Pi esteja sempre sincronizada com a branch `main`.

| Etapa | Ferramenta | Descrição |
| :--- | :--- | :--- |
| **Linting** | Super-Linter | Validação estática de sintaxe Python e arquivos YAML. |
| **Build** | Docker Buildx | Geração de imagem nativa **ARM64** para o Raspberry Pi. |
| **Registry** | GHCR.io | Armazenamento seguro da imagem no GitHub Container Registry. |
| **Transporte** | Tailscale + SCP | Transferência segura do `docker-stack.yml` via túnel VPN. |
| **Orquestração**| Docker Swarm | Atualização do serviço com `stack deploy` e pull da nova imagem. |

### 🚀 Detalhamento do Processo

1.  **Qualidade de Código**: O workflow inicia validando se não existem erros de formatação ou lógica básica que possam quebrar o build.
2.  **Integração Contínua (CI)**:
    * Utilizamos o **QEMU** para emular o ambiente ARM64 no Ubuntu do GitHub.
    * A imagem é buildada e enviada diretamente para o repositório de pacotes do GitHub.
3.  **Entrega Contínua (CD)**:
    * **Conexão**: O GitHub estabelece uma ponte segura com o Raspberry Pi via **Tailscale**.
    * **Sincronização**: O arquivo de configuração local é substituído pela versão do repositório via **SCP**.
    * **Deploy**: O comando `docker stack deploy` instrui o Swarm a realizar um *rolling update* do dashboard.
4.  **Exposição e Conectividade**:
    * **Porta Local**: O container responde na porta `8092`.
    * **Túnel Externo**: O **Cloudflare Tunnel** gerencia o tráfego de `https://shadow.greencity.net.br/` diretamente para o container, garantindo estabilidade para os WebSockets do Streamlit e eliminando a necessidade de proxies locais complexos.
5.  **Verificação de Saúde**: Um Health Check automático via `curl` confirma que a aplicação está online antes de finalizar o Job com sucesso.

---
<br>
<br>
<p align="center"> Desenvolvido por <strong>Pedro H. Alves de Souza Santos</strong> </p>
<p align="center"> <em>Engenharia de Software & Energia Sustentável</em> </p>