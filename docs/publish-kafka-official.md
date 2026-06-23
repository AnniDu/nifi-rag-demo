# PublishKafka 2.10.0

Source: https://nifi.apache.org/components/org.apache.nifi.kafka.processors.PublishKafka/
Source type: Official Apache NiFi component documentation

PublishKafka 2.10.0
  Bundle org.apache.nifi | nifi-kafka-nar Description Sends the contents of a FlowFile as either a message or as individual records to Apache Kafka using the Kafka Producer API. The messages to send may be individual FlowFiles, may be delimited using a user-specified delimiter (such as a new-line), or may be record-oriented data that can be read by the configured Record Reader. The complementary NiFi processor for fetching messages is ConsumeKafka. To produce a kafka tombstone message while using PublishStrategy.USE_WRAPPER, simply set the value of a record to 'null'. Tags Apache, Kafka, Message, PubSub, Put, Record, Send, avro, csv, json, logs Input Requirement  REQUIRED  Supports Sensitive Dynamic Properties false

Properties

-   Delivery Guarantee
Specifies the requirement for guaranteeing that a message is sent to Kafka. Corresponds to Kafka Client acks property.

  Display Name Delivery Guarantee Description Specifies the requirement for guaranteeing that a message is sent to Kafka. Corresponds to Kafka Client acks property. API Name acks Default Value all Allowable Values
-  Guarantee Replicated Delivery
-  Guarantee Single Node Delivery
-  Best Effort    Expression Language Scope Not Supported Sensitive false Required true

-   Compression Type
Specifies the compression strategy for records sent to Kafka. Corresponds to Kafka Client compression.type property.

  Display Name Compression Type Description Specifies the compression strategy for records sent to Kafka. Corresponds to Kafka Client compression.type property. API Name compression.type Default Value none Allowable Values
-  none
-  gzip
-  snappy
-  lz4
-  zstd    Expression Language Scope Not Supported Sensitive false Required true

-   Failure Strategy
Specifies how the processor handles a FlowFile if it is unable to publish the data to Kafka

  Display Name Failure Strategy Description Specifies how the processor handles a FlowFile if it is unable to publish the data to Kafka API Name Failure Strategy Default Value Route to Failure Allowable Values
-  Route to Failure
-  Rollback    Expression Language Scope Not Supported Sensitive false Required true

-   FlowFile Attribute Header Pattern
A Regular Expression that is matched against all FlowFile attribute names. Any attribute whose name matches the pattern will be added to the Kafka messages as a Header. If not specified, no FlowFile attributes will be added as headers.

  Display Name FlowFile Attribute Header Pattern Description A Regular Expression that is matched against all FlowFile attribute names. Any attribute whose name matches the pattern will be added to the Kafka messages as a Header. If not specified, no FlowFile attributes will be added as headers. API Name FlowFile Attribute Header Pattern Expression Language Scope Not Supported Sensitive false Required false

-   Header Encoding
For any attribute that is added as a Kafka Record Header, this property indicates the Character Encoding to use for serializing the headers.

  Display Name Header Encoding Description For any attribute that is added as a Kafka Record Header, this property indicates the Character Encoding to use for serializing the headers. API Name Header Encoding Default Value UTF-8 Expression Language Scope Environment variables and FlowFile Attributes Sensitive false Required true Dependencies
-  FlowFile Attribute Header Pattern is set to any value specified

-   Kafka Connection Service
Provides connections to Kafka Broker for publishing Kafka Records

  Display Name Kafka Connection Service Description Provides connections to Kafka Broker for publishing Kafka Records API Name Kafka Connection Service Service Interface org.apache.nifi.kafka.service.api.KafkaConnectionService Service Implementations
org.apache.nifi.kafka.service.aws.AmazonMSKConnectionService

org.apache.nifi.kafka.service.Kafka3ConnectionService
  Expression Language Scope Not Supported Sensitive false Required true

-   Kafka Key
The Key to use for the Message. If not specified, the FlowFile attribute 'kafka.key' is used as the message key, if it is present.Beware that setting Kafka key and demarcating at the same time may potentially lead to many Kafka messages with the same key.Normally this is not a problem as Kafka does not enforce or assume message and key uniqueness. Still, setting the demarcator and Kafka key at the same time poses a risk of data loss on Kafka. During a topic compaction on Kafka, messages will be deduplicated based on this key.

  Display Name Kafka Key Description The Key to use for the Message. If not specified, the FlowFile attribute 'kafka.key' is used as the message key, if it is present.Beware that setting Kafka key and demarcating at the same time may potentially lead to many Kafka messages with the same key.Normally this is not a problem as Kafka does not enforce or assume message and key uniqueness. Still, setting the demarcator and Kafka key at the same time poses a risk of data loss on Kafka. During a topic compaction on Kafka, messages will be deduplicated based on this key. API Name Kafka Key Expression Language Scope Environment variables and FlowFile Attributes Sensitive false Required false

-   Kafka Key Attribute Encoding
FlowFiles that are emitted have an attribute named 'kafka.key'. This property dictates how the value of the attribute should be encoded.

  Display Name Kafka Key Attribute Encoding Description FlowFiles that are emitted have an attribute named 'kafka.key'. This property dictates how the value of the attribute should be encoded. API Name Kafka Key Attribute Encoding Default Value utf-8 Allowable Values
-  UTF-8 Encoded
-  Hex Encoded
-  Do Not Add Key as Attribute    Expression Language Scope Not Supported Sensitive false Required true

-   Max Request Size
The maximum size of a request in bytes. Corresponds to Kafka Client max.request.size property.

  Display Name Max Request Size Description The maximum size of a request in bytes. Corresponds to Kafka Client max.request.size property. API Name max.request.size Default Value 1 MB Expression Language Scope Not Supported Sensitive false Required true

-   Message Demarcator
Specifies the string (interpreted as UTF-8) to use for demarcating multiple messages within a single FlowFile. If not specified, the entire content of the FlowFile will be used as a single message. If specified, the contents of the FlowFile will be split on this delimiter and each section sent as a separate Kafka message. To enter special character such as 'new line' use CTRL+Enter or Shift+Enter, depending on your OS.

  Display Name Message Demarcator Description Specifies the string (interpreted as UTF-8) to use for demarcating multiple messages within a single FlowFile. If not specified, the entire content of the FlowFile will be used as a single message. If specified, the contents of the FlowFile will be split on this delimiter and each section sent as a separate Kafka message. To enter special character such as 'new line' use CTRL+Enter or Shift+Enter, depending on your OS. API Name Message Demarcator Expression Language Scope Environment variables and FlowFile Attributes Sensitive false Required false

-   Message Key Field
The name of a field in the Input Records that should be used as the Key for the Kafka message.

  Display Name Message Key Field Description The name of a field in the Input Records that should be used as the Key for the Kafka message. API Name Message Key Field Expression Language Scope Environment variables and FlowFile Attributes Sensitive false Required false Dependencies
-  Publish Strategy is set to any of  [USE_VALUE]

-   Partition
Specifies the Kafka Partition destination for Records.

  Display Name Partition Description Specifies the Kafka Partition destination for Records. API Name partition Expression Language Scope Environment variables and FlowFile Attributes Sensitive false Required false

-   Partitioner Class
Specifies which class to use to compute a partition id for a message. Corresponds to Kafka Client partitioner.class property.

  Display Name Partitioner Class Description Specifies which class to use to compute a partition id for a message. Corresponds to Kafka Client partitioner.class property. API Name partitioner.class Default Value org.apache.kafka.clients.producer.internals.DefaultPartitioner Allowable Values
-  RoundRobinPartitioner
-  DefaultPartitioner
-  Expression Language Partitioner    Expression Language Scope Not Supported Sensitive false Required true

-   Publish Strategy
The format used to publish the incoming FlowFile record to Kafka.

  Display Name Publish Strategy Description The format used to publish the incoming FlowFile record to Kafka. API Name Publish Strategy Default Value USE_VALUE Allowable Values
-  Use Content as Record Value
-  Use Wrapper    Expression Language Scope Not Supported Sensitive false Required true Dependencies
-  Record Reader is set to any value specified

-   Record Key Writer
The Record Key Writer to use for outgoing FlowFiles

  Display Name Record Key Writer Description The Record Key Writer to use for outgoing FlowFiles API Name Record Key Writer Service Interface org.apache.nifi.serialization.RecordSetWriterFactory Service Implementations
org.apache.nifi.avro.AvroRecordSetWriter

org.apache.nifi.csv.CSVRecordSetWriter

org.apache.nifi.text.FreeFormTextRecordSetWriter

org.apache.nifi.json.JsonRecordSetWriter

org.apache.nifi.lookup.RecordSetWriterLookup

org.apache.nifi.record.script.ScriptedRecordSetWriter

org.apache.nifi.xml.XMLRecordSetWriter
  Expression Language Scope Not Supported Sensitive false Required false

-   Record Metadata Strategy
Specifies whether the Record's metadata (topic and partition) should come from the Record's metadata field or if it should come from the configured Topic Name and Partition / Partitioner class properties

  Display Name Record Metadata Strategy Description Specifies whether the Record's metadata (topic and partition) should come from the Record's metadata field or if it should come from the configured Topic Name and Partition / Partitioner class properties API Name Record Metadata Strategy Default Value FROM_PROPERTIES Allowable Values
-  Metadata From Record
-  Use Configured Values    Expression Language Scope Not Supported Sensitive false Required true Dependencies
-  Publish Strategy is set to any of  [USE_WRAPPER]

-   Record Reader
The Record Reader to use for incoming FlowFiles

  Display Name Record Reader Description The Record Reader to use for incoming FlowFiles API Name Record Reader Service Interface org.apache.nifi.serialization.RecordReaderFactory Service Implementations
org.apache.nifi.avro.AvroReader

org.apache.nifi.cef.CEFReader

org.apache.nifi.csv.CSVReader

org.apache.nifi.excel.ExcelReader

org.apache.nifi.grok.GrokReader

org.apache.nifi.json.JsonPathReader

org.apache.nifi.json.JsonTreeReader

org.apache.nifi.services.protobuf.ProtobufReader

org.apache.nifi.lookup.ReaderLookup

org.apache.nifi.record.script.ScriptedReader

org.apache.nifi.services.protobuf.StandardProtobufReader

org.apache.nifi.syslog.Syslog5424Reader

org.apache.nifi.syslog.SyslogReader

org.apache.nifi.windowsevent.WindowsEventLogReader

org.apache.nifi.xml.XMLReader

org.apache.nifi.yaml.YamlTreeReader
  Expression Language Scope Not Supported Sensitive false Required false

-   Record Writer
The Record Writer to use in order to serialize the data before sending to Kafka

  Display Name Record Writer Description The Record Writer to use in order to serialize the data before sending to Kafka API Name Record Writer Service Interface org.apache.nifi.serialization.RecordSetWriterFactory Service Implementations
org.apache.nifi.avro.AvroRecordSetWriter

org.apache.nifi.csv.CSVRecordSetWriter

org.apache.nifi.text.FreeFormTextRecordSetWriter

org.apache.nifi.json.JsonRecordSetWriter

org.apache.nifi.lookup.RecordSetWriterLookup

org.apache.nifi.record.script.ScriptedRecordSetWriter

org.apache.nifi.xml.XMLRecordSetWriter
  Expression Language Scope Not Supported Sensitive false Required false

-   Topic Name
Name of the Kafka Topic to which the Processor publishes Kafka Records

  Display Name Topic Name Description Name of the Kafka Topic to which the Processor publishes Kafka Records API Name Topic Name Expression Language Scope Environment variables and FlowFile Attributes Sensitive false Required true

-   Transactional ID Prefix
Specifies the KafkaProducer config transactional.id will be a generated UUID and will be prefixed with the configured string.

  Display Name Transactional ID Prefix Description Specifies the KafkaProducer config transactional.id will be a generated UUID and will be prefixed with the configured string. API Name Transactional ID Prefix Expression Language Scope Environment variables and FlowFile Attributes Sensitive false Required false Dependencies
-  Transactions Enabled is set to any of  [true]

-   Transactions Enabled
Specifies whether to provide transactional guarantees when communicating with Kafka. If there is a problem sending data to Kafka, and this property is set to false, then the messages that have already been sent to Kafka will continue on and be delivered to consumers. If this is set to true, then the Kafka transaction will be rolled back so that those messages are not available to consumers. Setting this to true requires that the [Delivery Guarantee] property be set to [Guarantee Replicated Delivery.]

  Display Name Transactions Enabled Description Specifies whether to provide transactional guarantees when communicating with Kafka. If there is a problem sending data to Kafka, and this property is set to false, then the messages that have already been sent to Kafka will continue on and be delivered to consumers. If this is set to true, then the Kafka transaction will be rolled back so that those messages are not available to consumers. Setting this to true requires that the [Delivery Guarantee] property be set to [Guarantee Replicated Delivery.] API Name Transactions Enabled Default Value true Allowable Values
-  true
-  false    Expression Language Scope Not Supported Sensitive false Required true

Relationships

  | Name  | Description

  | failure  | Any FlowFile that cannot be sent to Kafka will be routed to this Relationship

  | success  | FlowFiles for which all content was sent to Kafka.

Reads Attributes

  | Name  | Description

  | kafka.tombstone  | If this attribute is set to 'true', if the processor is not configured with a demarcator and if the FlowFile's content is null, then a tombstone message with zero bytes will be sent to Kafka.

Writes Attributes

  | Name  | Description

  | msg.count  | The number of messages that were sent to Kafka for this FlowFile. This attribute is added only to FlowFiles that are routed to success.

See Also

-  org.apache.nifi.kafka.processors.ConsumeKafka
