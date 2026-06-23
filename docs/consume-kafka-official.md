# ConsumeKafka 2.10.0

Source: https://nifi.apache.org/components/org.apache.nifi.kafka.processors.ConsumeKafka/
Source type: Official Apache NiFi component documentation

ConsumeKafka 2.10.0
  Bundle org.apache.nifi | nifi-kafka-nar Description Consumes messages from Apache Kafka Consumer API. The complementary NiFi processor for sending messages is PublishKafka. The Processor supports consumption of Kafka messages, optionally interpreted as NiFi records. Please note that, at this time (in read record mode), the Processor assumes that all records that are retrieved from a given partition have the same schema. For this mode, if any of the Kafka messages are pulled but cannot be parsed or written with the configured Record Reader or Record Writer, the contents of the message will be written to a separate FlowFile, and that FlowFile will be transferred to the 'parse.failure' relationship. Otherwise, each FlowFile is sent to the 'success' relationship and may contain many individual messages within the single FlowFile. A 'record.count' attribute is added to indicate how many messages are contained in the FlowFile. No two Kafka messages will be placed into the same FlowFile if they have different schemas, or if they have different values for a message header that is included by the <Headers to Add as Attributes> property. Tags Consume, Get, Ingest, Ingress, Kafka, PubSub, Record, Topic, avro, csv, json Input Requirement  FORBIDDEN  Supports Sensitive Dynamic Properties false
-  Additional Details for ConsumeKafka 2.10.0

### ConsumeKafka

### Output Strategies

This processor offers multiple output strategies (configured via processor property ‘Output Strategy’) for converting Kafka records into FlowFiles.

- ‘Use Content as Value’ (the default) emits FlowFile records containing only the Kafka record value.
- ‘Use Wrapper’ emits FlowFile records containing the Kafka record key, value, and headers, as well as additional metadata from the Kafka record.
- ‘Inject Metadata’ emits FlowFile records containing the Kafka record value into which a sub record field has been added to hold metadata, headers and key information.
The record schema that is used when “Use Wrapper” is selected is as follows (in Avro format):

{
  "type": "record",
  "name": "nifiRecord",
  "namespace": "org.apache.nifi",
  "fields": [{
      "name": "key",
      "type": [{
          < Schema is determined by the Key Record Reader, or will be "string" or "bytes", depending on the "Key Format" property (see below for more details) >
        }, "null"]
    },
    {
      "name": "value",
      "type": [
        {
          < Schema is determined by the Record Reader >
        },
        "null"
      ]
    },
    {
      "name": "headers",
      "type": [
        { "type": "map", "values": "string", "default": {}},
        "null"]
    },
    {
      "name": "metadata",
      "type": [
        {
          "type": "record",
          "name": "metadataType",
          "fields": [
            { "name": "topic", "type": ["string", "null"] },
            { "name": "partition", "type": ["int", "null"] },
            { "name": "offset", "type": ["int", "null"] },
            { "name": "timestamp", "type": ["long", "null"] }
          ]
        },
        "null"
      ]
    }
  ]
}

The record schema that is used when “Inject Metadata” is selected is as follows (in Avro format):

{
  "type": "record",
  "name": "nifiRecord",
  "namespace": "org.apache.nifi",
  "fields": [
      < Fields as determined by the Record Reader for the Kafka message >,
    {
      "name": "kafkaMetadata",
      "type": [
        {
          "type": "record",
          "name": "metadataType",
          "fields": [
            { "name": "topic", "type": ["string", "null"] },
            { "name": "partition", "type": ["int", "null"] },
            { "name": "offset", "type": ["int", "null"] },
            { "name": "timestamp", "type": ["long", "null"] },
            {
              "name": "headers",
              "type": [ { "type": "map", "values": "string", "default": {}}, "null"]
            },
            {
              "name": "key",
              "type": [{
                < Schema is determined by the Key Record Reader, or will be "string" or "bytes", depending on the "Key Format" property (see below for more details) >
              }, "null"]
            }
          ]
        },
        "null"
      ]
    }
  ]
}

If the Output Strategy property is set to ‘Use Wrapper’ or ‘Inject Metadata’, an additional processor configuration property (‘Key Format’) is activated. This property is used to specify how the Kafka Record’s key should be written out to the FlowFile. The possible values for ‘Key Format’ are as follows:

- ‘Byte Array’ supplies the Kafka Record Key as a byte array, exactly as they are received in the Kafka record.

- ‘String’ converts the Kafka Record Key bytes into a string using the UTF-8 character encoding. (Failure to parse the key bytes as UTF-8 will result in the record being routed to the ‘parse.failure’ relationship.)

- ‘Record’ converts the Kafka Record Key bytes into a deserialized NiFi record, using the associated ‘Key Record Reader’ controller service. If the Key Format property is set to ‘Record’, an additional processor configuration property name ‘Key Record Reader’ is made available. This property is used to specify the Record Reader to use in order to parse the Kafka Record’s key as a Record.

Here is an example of FlowFile content that is emitted by JsonRecordSetWriter when strategy “Use Wrapper” is selected:

[
  {
    "key": {
      "name": "Acme",
      "number": "AC1234"
    },
    "value": {
      "address": "1234 First Street",
      "zip": "12345",
      "account": {
        "name": "Acme",
        "number": "AC1234"
      }
    },
    "headers": {
      "attributeA": "valueA",
      "attributeB": "valueB"
    },
    "metadata": {
      "topic": "accounts",
      "partition": 0,
      "offset": 0,
      "timestamp": 0
    }
  }
]

Here is an example of FlowFile content that is emitted by JsonRecordSetWriter when strategy “Inject Metadata” is selected:

[
  {
    "address": "1234 First Street",
    "zip": "12345",
    "account": {
      "name": "Acme",
      "number": "AC1234"
    },
    "kafkaMetadata": {
      "topic": "accounts",
      "partition": 0,
      "offset": 0,
      "timestamp": 0,
      "headers": {
        "attributeA": "valueA",
        "attributeB": "valueB"
      },
      "key": {
        "name": "Acme",
        "number": "AC1234"
      }
    }
  }
]

Properties

-

                Auto Offset Reset

Automatic offset configuration applied when no previous consumer offset found corresponding to Kafka auto.offset.reset property

                    Display Name
                    Auto Offset Reset
                    Description
                    Automatic offset configuration applied when no previous consumer offset found corresponding to Kafka auto.offset.reset property
                    API Name
                    auto.offset.reset

                    Default Value
                    latest

                    Allowable Values

-
                                earliest

-
                                latest

-
                                none

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

-

                Commit Offsets

Specifies whether this Processor should commit the offsets to Kafka after receiving messages. Typically, this value should be set to true so that messages that are received are not duplicated. However, in certain scenarios, we may want to avoid committing the offsets, that the data can be processed and later acknowledged by PublishKafka in order to provide Exactly Once semantics.

                    Display Name
                    Commit Offsets
                    Description
                    Specifies whether this Processor should commit the offsets to Kafka after receiving messages. Typically, this value should be set to true so that messages that are received are not duplicated. However, in certain scenarios, we may want to avoid committing the offsets, that the data can be processed and later acknowledged by PublishKafka in order to provide Exactly Once semantics.
                    API Name
                    Commit Offsets

                    Default Value
                    true

                    Allowable Values

-
                                true

-
                                false

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

-

                Group ID

Kafka Consumer Group Identifier corresponding to Kafka group.id property

                    Display Name
                    Group ID
                    Description
                    Kafka Consumer Group Identifier corresponding to Kafka group.id property
                    API Name
                    Group ID

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

-

                Header Encoding

Character encoding applied when reading Kafka Record Header values and writing FlowFile attributes

                    Display Name
                    Header Encoding
                    Description
                    Character encoding applied when reading Kafka Record Header values and writing FlowFile attributes
                    API Name
                    Header Encoding

                    Default Value
                    UTF-8

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

-

                Header Name Pattern

Regular Expression Pattern applied to Kafka Record Header Names for selecting Header Values to be written as FlowFile attributes

                    Display Name
                    Header Name Pattern
                    Description
                    Regular Expression Pattern applied to Kafka Record Header Names for selecting Header Values to be written as FlowFile attributes
                    API Name
                    Header Name Pattern

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    false

-

                Header Name Prefix

A prefix to apply to the FlowFile attribute name when writing Kafka Record Header values.
This is useful to avoid conflicts with reserved FlowFile attribute names such as 'uuid'.
For example, if set to 'kafka.header.', a Kafka header named 'uuid' would be written as 'kafka.header.uuid'.

                    Display Name
                    Header Name Prefix
                    Description
                    A prefix to apply to the FlowFile attribute name when writing Kafka Record Header values.
This is useful to avoid conflicts with reserved FlowFile attribute names such as 'uuid'.
For example, if set to 'kafka.header.', a Kafka header named 'uuid' would be written as 'kafka.header.uuid'.

                    API Name
                    Header Name Prefix

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    false

                    Dependencies

-
                                Processing Strategy
                                is set to any

                                  of

                                [FLOW_FILE]

-

                Kafka Connection Service

Provides connections to Kafka Broker for publishing Kafka Records

                    Display Name
                    Kafka Connection Service
                    Description
                    Provides connections to Kafka Broker for publishing Kafka Records
                    API Name
                    Kafka Connection Service

                    Service Interface
                    org.apache.nifi.kafka.service.api.KafkaConnectionService

                    Service Implementations

org.apache.nifi.kafka.service.aws.AmazonMSKConnectionService

org.apache.nifi.kafka.service.Kafka3ConnectionService

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

-

                Key Attribute Encoding

Encoding for value of configured FlowFile attribute containing Kafka Record Key.

                    Display Name
                    Key Attribute Encoding
                    Description
                    Encoding for value of configured FlowFile attribute containing Kafka Record Key.
                    API Name
                    Key Attribute Encoding

                    Default Value
                    utf-8

                    Allowable Values

-
                                UTF-8 Encoded

-
                                Hex Encoded

-
                                Do Not Add Key as Attribute

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

-

                Key Format

Specifies how to represent the Kafka Record Key in the output FlowFile

                    Display Name
                    Key Format
                    Description
                    Specifies how to represent the Kafka Record Key in the output FlowFile
                    API Name
                    Key Format

                    Default Value
                    byte-array

                    Allowable Values

-
                                String

-
                                Byte Array

-
                                Record

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

                    Dependencies

-
                                Output Strategy
                                is set to any

                                  of

                                [INJECT_METADATA, USE_WRAPPER]

-

                Key Record Reader

The Record Reader to use for parsing the Kafka Record Key into a Record

                    Display Name
                    Key Record Reader
                    Description
                    The Record Reader to use for parsing the Kafka Record Key into a Record
                    API Name
                    Key Record Reader

                    Service Interface
                    org.apache.nifi.serialization.RecordReaderFactory

                    Service Implementations

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

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

                    Dependencies

-
                                Key Format
                                is set to any

                                  of

                                [record]

-

                Max Uncommitted Size

Maximum total size of records to consume from Kafka before transferring FlowFiles to an output
relationship. Evaluated when specified based on the size of serialized keys and values from each
Kafka record, before reaching the [Max Uncommitted Time].

                    Display Name
                    Max Uncommitted Size
                    Description
                    Maximum total size of records to consume from Kafka before transferring FlowFiles to an output
relationship. Evaluated when specified based on the size of serialized keys and values from each
Kafka record, before reaching the [Max Uncommitted Time].

                    API Name
                    Max Uncommitted Size

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    false

-

                Max Uncommitted Time

Maximum amount of time to spend consuming records from Kafka before transferring FlowFiles to an
output relationship. Longer amounts of time may produce larger FlowFiles and increase processing
latency for individual records.

                    Display Name
                    Max Uncommitted Time
                    Description
                    Maximum amount of time to spend consuming records from Kafka before transferring FlowFiles to an
output relationship. Longer amounts of time may produce larger FlowFiles and increase processing
latency for individual records.

                    API Name
                    Max Uncommitted Time

                    Default Value
                    100 millis

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

-

                Message Demarcator

Since KafkaConsumer receives messages in batches, this Processor has an option to output FlowFiles which contains all Kafka messages in a single batch for a given topic and partition and this property allows you to provide a string (interpreted as UTF-8) to use for demarcating apart multiple Kafka messages. This is an optional property and if not provided each Kafka message received will result in a single FlowFile which  time it is triggered. To enter special character such as 'new line' use CTRL+Enter or Shift+Enter depending on the OS

                    Display Name
                    Message Demarcator
                    Description
                    Since KafkaConsumer receives messages in batches, this Processor has an option to output FlowFiles which contains all Kafka messages in a single batch for a given topic and partition and this property allows you to provide a string (interpreted as UTF-8) to use for demarcating apart multiple Kafka messages. This is an optional property and if not provided each Kafka message received will result in a single FlowFile which  time it is triggered. To enter special character such as 'new line' use CTRL+Enter or Shift+Enter depending on the OS
                    API Name
                    Message Demarcator

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

                    Dependencies

-
                                Processing Strategy
                                is set to any

                                  of

                                [DEMARCATOR]

-

                Output Strategy

The format used to output the Kafka Record into a FlowFile Record.

                    Display Name
                    Output Strategy
                    Description
                    The format used to output the Kafka Record into a FlowFile Record.
                    API Name
                    Output Strategy

                    Default Value
                    USE_VALUE

                    Allowable Values

-
                                Use Content as Value

-
                                Use Wrapper

-
                                Inject Metadata

-
                                Inject Offset

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

                    Dependencies

-
                                Processing Strategy
                                is set to any

                                  of

                                [RECORD]

-

                Processing Strategy

Strategy for processing Kafka Records and writing serialized output to FlowFiles

                    Display Name
                    Processing Strategy
                    Description
                    Strategy for processing Kafka Records and writing serialized output to FlowFiles
                    API Name
                    Processing Strategy

                    Default Value
                    FLOW_FILE

                    Allowable Values

-
                                FLOW_FILE

-
                                DEMARCATOR

-
                                RECORD

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

-

                Record Reader

The Record Reader to use for incoming Kafka messages

                    Display Name
                    Record Reader
                    Description
                    The Record Reader to use for incoming Kafka messages
                    API Name
                    Record Reader

                    Service Interface
                    org.apache.nifi.serialization.RecordReaderFactory

                    Service Implementations

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

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

                    Dependencies

-
                                Processing Strategy
                                is set to any

                                  of

                                [RECORD]

-

                Record Writer

The Record Writer to use in order to serialize the outgoing FlowFiles

                    Display Name
                    Record Writer
                    Description
                    The Record Writer to use in order to serialize the outgoing FlowFiles
                    API Name
                    Record Writer

                    Service Interface
                    org.apache.nifi.serialization.RecordSetWriterFactory

                    Service Implementations

org.apache.nifi.avro.AvroRecordSetWriter

org.apache.nifi.csv.CSVRecordSetWriter

org.apache.nifi.text.FreeFormTextRecordSetWriter

org.apache.nifi.json.JsonRecordSetWriter

org.apache.nifi.lookup.RecordSetWriterLookup

org.apache.nifi.record.script.ScriptedRecordSetWriter

org.apache.nifi.xml.XMLRecordSetWriter

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

                    Dependencies

-
                                Processing Strategy
                                is set to any

                                  of

                                [RECORD]

-

                Separate By Key

When this property is enabled, two messages will only be added to the same FlowFile if both of the Kafka Messages have identical keys.

                    Display Name
                    Separate By Key
                    Description
                    When this property is enabled, two messages will only be added to the same FlowFile if both of the Kafka Messages have identical keys.
                    API Name
                    Separate By Key

                    Default Value
                    false

                    Allowable Values

-
                                true

-
                                false

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

                    Dependencies

-
                                Message Demarcator
                                is set to any

                                  value specified

-

                Topic Format

Specifies whether the Topics provided are a comma separated list of names or a single regular expression

                    Display Name
                    Topic Format
                    Description
                    Specifies whether the Topics provided are a comma separated list of names or a single regular expression
                    API Name
                    Topic Format

                    Default Value
                    names

                    Allowable Values

-
                                names

-
                                pattern

                    Expression Language Scope
                    Not Supported
                    Sensitive
                    false
                    Required
                    true

-

                Topics

The name or pattern of the Kafka Topics from which the Processor consumes Kafka Records. More than one can be supplied if comma separated.

                    Display Name
                    Topics
                    Description
                    The name or pattern of the Kafka Topics from which the Processor consumes Kafka Records. More than one can be supplied if comma separated.
                    API Name
                    Topics

                    Expression Language Scope
                    Environment variables defined at JVM level and system properties
                    Sensitive
                    false
                    Required
                    true

Relationships

             | Name
             | Description

             | success
             | FlowFiles containing one or more serialized Kafka Records

Writes Attributes

             | Name
             | Description

             | record.count
             | The number of records received

             | mime.type
             | The MIME Type that is provided by the configured Record Writer

             | kafka.count
             | The number of records in the FlowFile for a batch of records

             | kafka.key
             | The key of message if present and if single message. How the key is encoded depends on the value of the 'Key Attribute Encoding' property.

             | kafka.offset
             | The offset of the record in the partition or the minimum value of the offset in a batch of records

             | kafka.timestamp
             | The timestamp of the message consumed from the topic or the minimum value of the timestamp in a batch of messages. The value of this timestamp depends on 'log.message.timestamp.type` kafka broker config (LOG_APPEND_TIME, CREATE_TIME, NO_TIMESTAMP_TYPE)

             | kafka.partition
             | The partition of the topic for a record or batch of records

             | kafka.topic
             | The topic the for a record or batch of records

             | kafka.tombstone
             | Set to true if the consumed message is a tombstone message

             | kafka.max.offset
             | The maximum value of the Kafka offset in batch of records

See Also

-
        org.apache.nifi.kafka.processors.PublishKafka
