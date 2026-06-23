# HDFS / Hadoop Official Processor Examples and Additional Details

Source type: Official Apache NiFi component documentation
NiFi bundle: org.apache.nifi / nifi-hadoop-nar / 2.6.0

## ListHDFS

Source: https://nifi.apache.org/docs/nifi-docs/components/org.apache.nifi/nifi-hadoop-nar/2.6.0/org.apache.nifi.processors.hadoop.ListHDFS/additionalDetails.html

Examples:
 For the given examples, the following directory structure is used:

 data
 ├── readme.txt
 ├── bin
 │ ├── readme.txt
 │ ├── 1.bin
 │ ├── 2.bin
 │ └── 3.bin
 ├── csv
 │ ├── readme.txt
 │ ├── 1.csv
 │ ├── 2.csv
 │ └── 3.csv
 └── txt
 ├── readme.txt
 ├── 1.txt
 ├── 2.txt
 └── 3.txt

### Directories and Files
 This mode is useful when the listing should match the names of directories and files with the regular expression defined in
File Filter. When
Recurse Subdirectories is true, this mode allows the user to filter for files in subdirectories with names that match the regular expression defined in
File Filter.

 ListHDFS configuration:
 |
Property |
Value

 |
Directory |
/data

 |
Recurse Subdirectories | true
 |
File Filter |
.*txt.*

 |
Filter Mode |
Directories and Files

ListHDFS results:
- /data/readme.txt
- /data/txt/readme.txt
- /data/txt/1.txt
- /data/txt/2.txt
- /data/txt/3.txt

### Files Only
 This mode is useful when the listing should match only the names of files with the regular expression defined in
File Filter. Directory names will not be matched against the regular expression defined in
File Filter. When
Recurse Subdirectories is true, this mode allows the user to filter for files in the entire subdirectory tree of the directory specified in the
Directory property.

 ListHDFS configuration:
 |
Property |
Value

 |
Directory |
/data

 |
Recurse Subdirectories | true
 |
File Filter |
[^\.].*\.txt

 |
Filter Mode |
Files Only

ListHDFS results:
- /data/readme.txt
- /data/bin/readme.txt
- /data/csv/readme.txt
- /data/txt/readme.txt
- /data/txt/1.txt
- /data/txt/2.txt
- /data/txt/3.txt

### Full Path
 This mode is useful when the listing should match the entire path of a file with the regular expression defined in
File Filter. When
Recurse Subdirectories is true, this mode allows the user to filter for files in the entire subdirectory tree of the directory specified in the
Directory property while allowing filtering based on the full path of each file.

 ListHDFS configuration:
 |
Property |
Value

 |
Directory |
/data

 |
Recurse Subdirectories | true
 |
File Filter |
(/.*/)*csv/.*

 |
Filter Mode |
Full Path

ListHDFS results:
- /data/csv/readme.txt
- /data/csv/1.csv
- /data/csv/2.csv
- /data/csv/3.csv

### Streaming Versus Batch Processing

 ListHDFS performs a listing of all files that it encounters in the configured HDFS directory. There are two common, broadly defined use cases.

### Streaming Use Case

 By default, the Processor will create a separate FlowFile for each file in the directory and add attributes for filename, path, etc. A common use case is to connect ListHDFS to the FetchHDFS processor. These two processors used in conjunction with one another provide the ability to easily monitor a directory and fetch the contents of any new file as it lands in HDFS in an efficient streaming fashion.

### Batch Use Case

 Another common use case is the desire to process all newly arriving files in a given directory, and to then perform some action only when all files have completed their processing. The above approach of streaming the data makes this difficult, because NiFi is inherently a streaming platform in that there is no "job" that has a beginning and an end. Data is simply picked up as it becomes available.

 To solve this, the ListHDFS Processor can optionally be configured with a Record Writer. When a Record Writer is configured, a single FlowFile will be created that will contain a Record for each file in the directory, instead of a separate FlowFile per file. See the documentation for ListFile for an example of how to build a dataflow that allows for processing all of the files before proceeding with any other step.

 One important difference between the data produced by ListFile and ListHDFS, though, is the structure of the Records that are emitted. The Records emitted by ListFile have a different schema than those emitted by ListHDFS. ListHDFS emits records that follow the following schema (in Avro format):

{
  "type": "record",
  "name": "nifiRecord",
  "namespace": "org.apache.nifi",
  "fields": [{
    "name": "filename",
    "type": "string"
  }, {
    "name": "path",
    "type": "string"
  }, {
    "name": "directory",
    "type": "boolean"
  }, {
    "name": "size",
    "type": "long"
  }, {
    "name": "lastModified",
    "type": {
      "type": "long",
      "logicalType": "timestamp-millis"
    }
  }, {
    "name": "permissions",
    "type": ["null", "string"]
  }, {
    "name": "owner",
    "type": ["null", "string"]
  }, {
    "name": "group",
    "type": ["null", "string"]
  }, {
    "name": "replication",
    "type": ["null", "int"]
  }, {
    "name": "symLink",
    "type": ["null", "boolean"]
  }, {
    "name": "encrypted",
    "type": ["null", "boolean"]
  }, {
    "name": "erasureCoded",
    "type": ["null", "boolean"]
  }]
}

---

## PutHDFS

Source: https://nifi.apache.org/docs/nifi-docs/components/org.apache.nifi/nifi-hadoop-nar/2.6.0/org.apache.nifi.processors.hadoop.PutHDFS/additionalDetails.html

PutHDFS

### SSL Configuration:

 Hadoop provides the ability to configure keystore and/or truststore properties. If you want to use SSL-secured file system like swebhdfs, you can use the Hadoop configurations instead of using SSL Context Service.
- create 'ssl-client.xml' to configure the truststores.
ssl-client.xml Properties:

  | Property  | Default Value  | Explanation

  | ssl.client.truststore.type  | jks  | Truststore file type

  | ssl.client.truststore.location  | NONE  | Truststore file location

  | ssl.client.truststore.password  | NONE  | Truststore file password

  | ssl.client.truststore.reload.interval  | 10000  | Truststore reload interval, in milliseconds

ssl-client.xml Example:

<configuration>
  <property>
    <name>ssl.client.truststore.type</name>
    <value>jks</value>
  </property>
  <property>
    <name>ssl.client.truststore.location</name>
    <value>/path/to/truststore.jks</value>
  </property>
  <property>
    <name>ssl.client.truststore.password</name>
    <value>clientfoo</value>
  </property>
  <property>
    <name>ssl.client.truststore.reload.interval</name>
    <value>10000</value>
  </property>
</configuration>

- put 'ssl-client.xml' to the location looked up in the classpath, like under NiFi conriguration directory.

- set the name of 'ssl-client.xml' to hadoop.ssl.client.conf in the 'core-site.xml' which HDFS processors use.

<configuration>
    <property>
      <name>fs.defaultFS</name>
      <value>swebhdfs://{namenode.hostname:port}</value>
    </property>
    <property>
      <name>hadoop.ssl.client.conf</name>
      <value>ssl-client.xml</value>
    </property>
<configuration>
