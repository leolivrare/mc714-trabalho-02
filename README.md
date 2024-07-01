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

### Detalhes do Código:

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

### Testes Automatizados

**Setup do Kafka para os Testes**
```
class KafkaTestCase(unittest.TestCase):
    """
    A test case class for testing Kafka functionality.

    This class provides setup and teardown methods for creating and deleting a unique Kafka topic,
    as well as initializing a Kafka producer and consumer for testing purposes.
    """

    def setUp(self):
        conf = {"bootstrap.servers": "broker:29092"}
        self.producer = Producer(conf)
        self.consumer = Consumer(
            {
                "bootstrap.servers": "broker:29092",
                "group.id": "test",
                "auto.offset.reset": "earliest",
            }
        )

        # Create a unique topic
        self.topic = f"lamport_test_{uuid.uuid4()}"
        self.admin_client = AdminClient(conf)
        topic_config = {"num_partitions": 1, "replication_factor": 1}
        self.admin_client.create_topics([NewTopic(self.topic, **topic_config)])

        # Wait for the topic to be created
        while self.topic not in self.admin_client.list_topics().topics:
            time.sleep(1)

    def tearDown(self):
        self.consumer.close()

        # Delete the unique topic
        self.admin_client.delete_topics([self.topic])
```

Esse código faz o setuo do Kafka para o ambiente de testes automatizados. Ele basicamente define o produtor, consumidor e cria o tópico para receber as mensagens dos testes.

**Teste do Produtor**:
```
class TestProduceMessages(KafkaTestCase):
    def test_produce_messages(self):
        process_id = "Process_1234"
        lamport_time = 0

        expected_message = {"process_id": process_id, "lamport_time": lamport_time + 1}

        produce_messages(self.producer, self.topic, process_id, lamport_time)

        # Subscribe to the topic
        self.consumer.subscribe([self.topic])

        # Consume the message
        msg = self.consumer.poll(10.0)

        if msg is None:
            self.fail("No message received")
        elif not msg.error():
            received_message = json.loads(msg.value().decode("utf-8"))
            self.assertEqual(received_message, expected_message)
        elif msg.error().code() != KafkaError._PARTITION_EOF:
            self.fail(msg.error())
```

Esse teste valida se o produtor está funcionando corretamente, inclusive se está incrementando o relógio lógico corretamente.

**Testes do Consumidor**:
```
class TestConsumeMessages(KafkaTestCase):
    def test_consumer_selects_producers_lamport_time(self):
        process_id_producer = "Process_1"
        process_id_consumer = "Process_2"
        consumer_lamport_time = 0
        producer_lamport_time = 10

        # Increment producer's Lamport time by 1
        produce_messages(
            self.producer, self.topic, process_id_producer, producer_lamport_time
        )

        expected_message = {
            "process_id": process_id_producer,
            "lamport_time": producer_lamport_time + 1,
        }

        # Subscribe to the topic
        self.consumer.subscribe([self.topic])

        (msg, new_lamport_time) = consume_message(
            self.consumer, process_id_consumer, consumer_lamport_time
        )

        assert msg == expected_message

        assert new_lamport_time == producer_lamport_time + 2

    def test_consumer_selects_consumers_lamport_time(self):
        process_id_producer = "Process_1"
        process_id_consumer = "Process_2"
        consumer_lamport_time = 5
        producer_lamport_time = 0

        # Increment producer's Lamport time by 1
        produce_messages(
            self.producer, self.topic, process_id_producer, producer_lamport_time
        )

        expected_message = {
            "process_id": process_id_producer,
            "lamport_time": producer_lamport_time + 1,
        }

        # Subscribe to the topic
        self.consumer.subscribe([self.topic])

        (msg, new_lamport_time) = consume_message(
            self.consumer, process_id_consumer, consumer_lamport_time
        )

        assert msg == expected_message

        assert new_lamport_time == consumer_lamport_time + 1
```

Esse conjunto de testes valida o funcionamento do consumidor e da lógica de atualização do Lamport Time baseado nas mensagens recebidas. Esse teste garante que as mensagens do kafka estão sendo consumidas corretamente e o relógio lógico está sendo atualizado corretamente.

## Detalhes de Implementação do Algoritmo e Simulação do Problema de Exclusão Mútua

### Bibliotecas e Ambiente de Execução:
O algoritmo de Exclusão Mútua foi inteiramente implementado em Python, com o Kafka Confluent como broker de mensagens. Reutilizamos toda a implementação do algoritmo do Relógio Lógico de Lamport para implementar a lógica de Exclusão Mútua. Isto é, resolvemos o problema da Exclusão Mútua com o Relógio Lógico de Lamport fazendo o controle da ordem dos eventos, onde temos bem definido quem solicitou primeiro para acessar uma seção crítica.
Escolhemos por implementar usando docker para simplificar testes locais, porém é muito simples subir todos os containers num ambiente cloud. Por exemplo, podemos criar as imagens docker e subir os sistemas numa EC2 da AWS, subindo as imagens docker personalizadas via ECR.

**Bibliotecas Externas Utilizadas**:
- **confluent_kafka**: Biblioteca que possibilita a publicação e consumo de mensagens dos tópicos do Kafka.
- **pytest**: Biblioteca utilizada para execução dos testes automatizados do projeto.

### Estrutura de comunicação:
*Importante: Essa estrutura é exatamente a mesma da implementação anterior. Toda a dinâmica de troca de mensagens via Kafka e atualização do relógio lógico foram reaproveitados*

![image](https://github.com/leolivrare/mc714-trabalho-02/assets/47697560/3a6db8a0-e20e-49d0-8a2d-e08b4c29d3b7)
*Figura 03: Estrutura de comunicação na simulação de Exclusão Mútua*

### Detalhes do Código:

**Lógica de solicitar acesso a uma região crítica**:
```
def request_critical_section(
    producer, consumer, process_id, lamport_time, message_queue
):
    logger.info(f"Process {process_id} is requesting critical section.")
    lamport_time = produce_messages(
        producer,
        "mutual_exclusion_test_1",
        process_id,
        lamport_time,
        content={"event": "request"},
    )

    message_queue.append({"lamport_time": lamport_time, "process_id": process_id})
    sort_message_queue(message_queue)
    logger.info(f"Process {process_id} updated message queue: {message_queue}")

    acknowledged = set()

    while True:
        message, lamport_time = consume_message(consumer, process_id, lamport_time)

        if message is not None:
            if message["process_id"] == process_id:
                continue

            event = message["event"]
            sender_id = message["process_id"]
            sender_time = message["lamport_time"]

            if event == "reply":
                acknowledged.add(sender_id)

            elif event == "request":
                message_queue.append(
                    {"lamport_time": sender_time, "process_id": sender_id}
                )
                sort_message_queue(message_queue)
                logger.info(
                    f"Process {process_id} updated message queue: {message_queue}"
                )

                lamport_time = produce_messages(
                    producer,
                    "mutual_exclusion_test_1",
                    process_id,
                    lamport_time,
                    content={"event": "reply"},
                )

            elif event == "release":
                try:
                    remove_from_queue(message_queue, sender_id)
                    sort_message_queue(message_queue)
                    logger.info(
                        f"Process {process_id} updated message queue: {message_queue}"
                    )
                except ValueError:
                    pass
        logger.info(f"Process {process_id} updated acknowledged: {acknowledged}")
        if (
            message_queue[0]["process_id"] == process_id and len(acknowledged) == 2
        ):  # Assuming there are 3 processes in total
            break

    logger.info(f"Process {process_id} is entering critical section.")
    time.sleep(random.randint(1, 5))

    message_queue.pop(0)
    logger.info(f"Process {process_id} updated message queue: {message_queue}")

    lamport_time = produce_messages(
        producer,
        "mutual_exclusion_test_1",
        process_id,
        lamport_time,
        content={"event": "release"},
    )

    logger.info(f"Process {process_id} has left critical section.")
    return lamport_time, message_queue
```

Esse código é responsável por toda a lógica da exclusão mútua. Basicamente, ele funciona da seguinte forma:
- Cada processo tem seu próprio relógio lógico e sua fila de pedidos
- Quando um processo deseja acessar uma região crítica, ele envia uma mensagem no Kafka do tipo "request", junto com seu lamport_time. Além disso, ele adiciona seu pedido na fila e ordena ela pelo lamport_time e process_id.
- Quando um outro processo recebe a mensagem de "request", deve enviar uma mensagem de "OK" para o pedido e atualizar seu relógio lógico
- Quando o processo que solicitou o acesso recebe OK de todos os demais processos e seu pedido é o primeiro da fila, ele acessa a região crítica.
- Quando o processo sai da região crítica, ele deve publicar uma mensagem de "release" no Kafka e remover seu pedido da fila.
- Quando um processo recebe uma mensagem de "release", deve remover aquele pedido em questão da fila


### Testes Automatizados:

**Teste do Código de pedido de acesso à Região Crítica**:
```
class TestRequestCriticalSection(KafkaTestCase):
    def test_request_critical_section(self):
        process_id = 1
        lamport_time = 0
        message_queue = []

        # Subscribe to the topic
        self.consumer.subscribe([self.topic])

        produce_messages(self.producer, self.topic, 2, lamport_time+1, content={"event": "reply"})
        produce_messages(self.producer, self.topic, 3, lamport_time+1, content={"event": "reply"})

        # Alterar para ser uma chamada async
        lamport_time, message_queue = request_critical_section(self.producer, self.consumer, process_id, lamport_time, message_queue)

        # Analisa as variaveis lamport_time e message_queue após a execução da função request_critical_section. 
        self.assertEqual(lamport_time, 5)
        self.assertEqual(len(message_queue), 0)

    def test_request_critical_section_with_more_requests(self):
        process_id = 1
        lamport_time = 0
        message_queue = []

        # Subscribe to the topic
        self.consumer.subscribe([self.topic])

        produce_messages(self.producer, self.topic, 2, lamport_time+1, content={"event": "request"})
        produce_messages(self.producer, self.topic, 3, lamport_time+2, content={"event": "request"})
        produce_messages(self.producer, self.topic, 2, lamport_time+3, content={"event": "reply"})
        produce_messages(self.producer, self.topic, 3, lamport_time+4, content={"event": "reply"})

        # Alterar para ser uma chamada async
        lamport_time, message_queue = request_critical_section(self.producer, self.consumer, process_id, lamport_time, message_queue)

        # Analisa as variaveis lamport_time e message_queue após a execução da função request_critical_section. 
        self.assertEqual(lamport_time, 9)

        expected_queue = [{"lamport_time": 2, "process_id": 2}, {"lamport_time": 3, "process_id": 3}]
        assert expected_queue == message_queue
```

Esse conjunto de testes garante o funcionamento correto da função que solicita acesso a uma região crítica. Basicamente, validamos se o lamport_time foi atualizado corretamente e se o processo acessou a região crítica corretamente.

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
