# ConsumeKafka Official Output Examples

Source: https://nifi.apache.org/components/org.apache.nifi.kafka.processors.ConsumeKafka/
Source type: Official Apache NiFi component documentation

These examples are extracted from the official ConsumeKafka additional details section.

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

---

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
