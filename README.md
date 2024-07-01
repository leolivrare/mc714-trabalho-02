# mc714-trabalho-02

## Objetivo

Este projeto tem como objetivo apresentar uma implementação do algoritmo do Relógio Lógico de Lamport e uma implementação de um algoritmo de Exclusão Mútua. Ambas implementações incluem uma simulação para demonstrar o funcionamento dos algoritmos, onde a simulação do Relógio Lógico de Lamport simula dois processos independentes e a simulação da Exclusão Mútua simula três processos independentes.

A comunicação entre os processos é realizada através do Kafka, um broker de mensagens amplamente utilizado no mercado. Todo o código é escrito em Python e os processos e o broker são isolados em containers Docker separados.

## Descrição do Relógio Lógico de Lamport

O Relógio Lógico de Lamport é uma solução para o problema de ordenação de eventos em um sistema distribuído. Este algoritmo, proposto por Leslie Lamport, permite que todos os processos em um sistema distribuído possam concordar sobre a ordem dos eventos, mesmo na ausência de um relógio global.

**Funcionamento**:

- Cada processo possui um contador local (relógio).
- Evento local: o contador é incrementado.
- Envio de mensagem: o timestamp recebe o valor do contador e é enviado com a mensagem.
- Recepção de mensagem:
    - Se o timestamp for maior que o contador local, o contador local é atualizado para o valor máximo (timestamp ou contador local).
    - O contador local é incrementado.
    
**Resultado**:

- Os processos concordam com a ordem dos eventos, mesmo sem um relógio global.

**Vantagens**:

- Simplicidade e eficiência.
- Não há necessidade de um relógio global.

**Desvantagens**:

- Imprecisão em relação ao tempo real.
- Não garante ordenação total em todos os casos.

## Descrição do problema da Exclusão Mútua

A Exclusão Mútua é um problema clássico em sistemas distribuídos, onde vários processos precisam acessar um recurso compartilhado, mas apenas um processo pode acessar o recurso de cada vez. O algoritmo do Relógio Lógico de Lamport pode ser usado para resolver este problema.

**Funcionamento**:

1. Solicitação para entrar na seção crítica:
   - Enviar mensagem com timestamp para todos os outros processos.
2. Permissão para entrar:
   - Só pode entrar se:
     - Recebeu resposta de todos os outros processos.
     - Não há outra solicitação pendente com timestamp menor.
3. Garantias:
   - Apenas um processo na seção crítica por vez.
   - Ordem das solicitações é respeitada.

**Vantagens**:

- Evita conflitos de acesso.
- Garante ordenação justa.

**Desvantagens**:

- Implementação mais complexa.
- Pode haver atrasos na espera por respostas.

## Como executar o Projeto

### Requisitos:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

**Build do Projeto completo**
```
make build-all
```

### Configurar a instância do Kafka Confluent
*Importante: A instância do Kafka Confluent é a mesma para a simulação do Relógio Lógico de Lamport e a da Exclusão Mútua.*

**Para executar o Kafka (caso já tenha sido feito o build):**
```
make run-kafka
```

**Para visualizar se todos os containers estão UP and Running:**
```
docker-compose ps
```

Se tudo ocorreu bem, todos os containers do Kafka Confluent vão estão rodando e prontos para uso.

### Executar o projeto de Simulação do Algoritmo do Relógio Lógico de Lamport


## Referências

1. Algoritmo do Relógio Lógico de Lamport: https://www.geeksforgeeks.org/lamports-logical-clock/
2. Algoritmo de Exclusão Mútua com Relógio Lógico de Lamport: https://www.geeksforgeeks.org/lamports-algorithm-for-mutual-exclusion-in-distributed-system/
3. Kafka Confluent Docker Setup: https://docs.confluent.io/platform/current/platform-quickstart.html
4. GitHub Copilot para dúvidas e aceleração na escrita do código.

**Uso das referências**:

- O algoritmo descrito na referência [1] me ajudou a construir a lógica que foi aplicada no projeto. Porém, nenhum código foi copiado da referência, apenas o algoritmo descrito no texto. Isto é, o código final do Relógio Lógico de Lamport foi inteiramente construído por mim, utilizando o GitHub Copilot apenas para acelerar na escrita e ajustes de sintaxe.
- O algoritmo descrito na referência [2] me ajudou a construir a lógica que faz a Exclusão Mútua funcionar. Reutilizei quase todo o código do Relógio Lógico de Lamport, construído na primeira parte do projeto, para viabilizar essa implementação.
- O docker-compose teve como base a documentação do Kafka Confluent, indicado na referência [3]. Toda a parte que levanta o broker de mensagens foi retirado inteiramente da documentação.
- O GitHub Copilot (referência [4]) foi utilizado para acelerar a escrita do código e consulta de dúvidas. Porém, nenhuma informação foi utilizada sem validação e confirmação de fontes confiáveis.