# 🧹 Aspirador de Pó Inteligente: Agente Baseado em Estados vs. LLM

Este projeto implementa uma simulação de um agente inteligente (aspirador de pó) encarregado de limpar uma sequência de quartos interconectados. O projeto serve como um estudo comparativo no campo da Inteligência Artificial, apresentando duas abordagens para a tomada de decisão do agente:
1. **`AgenteIA` (Abordagem Tradicional):** Um agente baseado em regras lógicas hardcoded (estruturas condicionais padrão).
2. **`AgenteIA_LLM` (Abordagem com LLM):** Um agente que utiliza um modelo de linguagem local via Ollama (`deepseek-r1:7b`) com saídas estruturadas em JSON para decidir a próxima ação.

## 🚀 Funcionalidades

* **Geração Dinâmica de Ambientes:** Define uma quantidade customizada de quartos (de 'a' até 'o') iniciados no estado sujo (`"s"`).
* **Posicionamento Aleatório:** O aspirador inicia em um quarto aleatório.
* **Mapeamento de Estado Interno:** O agente mantém um histórico do que já visitou e do status conhecido de cada cômodo (`"i"` para desconhecido, `"s"` para sujo, `"l"` para limpo).
* **Saída Estruturada (JSON Schema):** Garante que o modelo LLM responda estritamente no formato esperado pelo código Python, evitando quebras de execução.

---

## 🛠️ Pré-requisitos

Para rodar a versão com LLM (`AgenteIA_LLM`), você precisará do **Ollama** instalado no seu sistema e do modelo correspondente baixado.

1. Baixe e instale o [Ollama](https://ollama.com/).
2. No terminal, baixe o modelo especificado no código:
   
```bash
   ollama pull deepseek-r1:7b