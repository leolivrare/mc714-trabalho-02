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
