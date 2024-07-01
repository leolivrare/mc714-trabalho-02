# Trabalho 02 de Sistemas Distribuidos (MC714)

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

### Build do Projeto
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

**Para criar o tópico no Kafka:**
```
make create-lamport-topic
```

**Para levantar os dois processos e iniciar a simulação:**
```
make run-lamport-apps
```

**Para visualizar os logs dos processos em execução:**
```
make logs-lamport-apps
make logs-lamport-app1
make logs-lamport-app2
```

**Para parar os processos em execução:**
```
make stop-lamport-apps
```

**Para executar os testes automatizados:**
```
make run-lamport-tests
```

### Executar o projeto de Simulação do Problema de Exclusão Mútua

**Para criar o tópico no Kafka:**
```
make create-mutual-exclusion-topic
```

**Para levantar os três processos e iniciar a simulação:**
```
make run-mutual-exclusion-apps
```

**Para visualizar os logs dos processos em execução:**
```
make logs-mutual-exclusion-apps
make logs-mutual-exclusion-app1
make logs-mutual-exclusion-app2
make logs-mutual-exclusion-app3
```

**Para parar os processos em execução:**
```
make stop-mutual-exclusion-apps
```

**Para executar os testes automatizados:**
```
make run-mutual-exclusion-tests
```

## Detalhes de Implementação do Algoritmo e Simulação do Relógio Lógico de Lamport

### Bibliotecas e Ambiente de Execução:
O algoritmo do Relógio Lógico de Lamport foi inteiramente implementado em Python, com o Kafka Confluent como broker de mensagens.
Simulamos o funcionamento do algoritmo com dois processos independentes, interagindo através de troca de mensagens pelo Kafka. Os dois processos e o broker foram executados em containers Docker, de forma que fossem completamente independentes uns dos outros.
Escolhemos por implementar usando docker para simplificar testes locais, porém é muito simples subir todos os containers num ambiente cloud. Por exemplo, podemos criar as imagens docker e subir os sistemas numa EC2 da AWS, subindo as imagens docker personalizadas via ECR.

**Bibliotecas Externas Utilizadas**:
- **confluent_kafka**: Biblioteca que possibilita a publicação e consumo de mensagens dos tópicos do Kafka.
- **pytest**: Biblioteca utilizada para execução dos testes automatizados do projeto.

### Estrutura de comunicação:
![lamport_clock: estrutura de comunicacao](https://github.com/leolivrare/mc714-trabalho-02/assets/47697560/f91a0d0d-e546-45b8-b613-333eef292b3b)
*Figura 01: Estrutura de comunicação entre os processos e o broker de mensagens.*

### Exemplo de fluxo de atualização do relógio lógico:
![lamport_clock: fluxo de exemplo](https://github.com/leolivrare/mc714-trabalho-02/assets/47697560/b9e2ff1b-1ef7-436a-ae8c-ccf8798327e3)
*Figura 02: Exemplo do fluxo de atualização do relógio lógico.*

### Código que faz a atualização do relógio lógico e a comunicação com o Kafka:

**Produtor**:
```
def produce_messages(
    producer: Producer,
    topic: str,
    process_id: int,
    lamport_time: int,
    content: Dict[str, Any] = {},
) -> int:
    """
    Produces a message to a Kafka topic using the provided producer.

    Args:
        producer (Producer): The Kafka producer instance.
        topic (str): The name of the Kafka topic to produce the message to.
        process_id (int): The ID of the process producing the message.
        lamport_time (int): The current Lamport time.
        content (Dict[str, Any], optional): Additional content to include in the message. Defaults to {}.

    Returns:
        int: The updated Lamport time after producing the message.
    """
    lamport_time += 1
    message = {"process_id": process_id, "lamport_time": lamport_time}
    message.update(content)
    producer.poll(0)
    producer.produce(
        topic, json.dumps(message).encode("utf-8"), callback=delivery_report
    )
    producer.flush()
    return lamport_time
```

**Consumidor**:
```
def consume_message(
    consumer: Consumer, process_id: int, lamport_time: int
) -> Tuple[Dict[str, Any], int]:
    """
    Consume a message from the Kafka consumer and update the Lamport time.

    Args:
        consumer (Consumer): The Kafka consumer instance.
        process_id (int): The ID of the current process.
        lamport_time (int): The current Lamport time.

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing the consumed message and the updated Lamport time.
    """
    msg = consumer.poll(1.0)
    message = None
    if msg is not None and not msg.error():
        try:
            message = json.loads(msg.value().decode("utf-8"))
            received_process_id = message["process_id"]
            received_lamport_time = int(message["lamport_time"])

            if received_process_id != process_id:
                last_lamport_time = lamport_time
                lamport_time = max(last_lamport_time, received_lamport_time) + 1

                log_message = {
                    "event": f"Received message from process {received_process_id} with Lamport time {received_lamport_time}. Updated Lamport time: max({last_lamport_time}, {received_lamport_time})+1 = {lamport_time}",
                    "lamport_time": lamport_time,
                }
                logger.info(json.dumps(log_message))
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")

    elif msg is not None:
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                logger.error(msg.error())

    return (message, lamport_time)
```

**Código que simula o envio e recebimento de mensagens**:
```
def simulate_lamport_clock(producer, consumer, process_id):
    """
    Simulates the Lamport logical clock for a given process.

    Args:
        producer: The producer object used to send messages.
        consumer: The consumer object used to receive messages.
        process_id: The ID of the current process.

    Returns:
        None
    """
    lamport_time = 0
    while True:
        start_time = time.time()
        produce_time = random.randint(1, 3)
        while time.time() - start_time < produce_time:
            lamport_time = produce_messages(
                producer, "lamport_test_1", process_id, lamport_time
            )
            time.sleep(1)

        start_time = time.time()
        consume_time = random.randint(2, 5)
        while time.time() - start_time < consume_time:
            (_, lamport_time) = consume_message(consumer, process_id, lamport_time)
```


Toda a lógica de funcionamento do Relógio Lógico de Lamport está dentro do consumidor e produtor de mensagens para o Kafka. Toda nova mensagem produzida o algoritmo incrementa o relógio e em cada mensagem consumida o algoritmo aplica a lógica de escolher entre o maior timestamp e incrementa um sobre ele.

Além disso, temos uma função chamada "simulate_lamport_clock" que serve para simular o funcionamento de um processo independente. Isto é, ele varia as ações do processo entre consumir mensagens do kafka e produzir novas mensagens, assim teremos uma simulação de como o Relógio Lógico é atualizado ao longo do tempo.

## Detalhes de Implementação do Algoritmo e Simulação do Problema de Exclusão Mútua

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
