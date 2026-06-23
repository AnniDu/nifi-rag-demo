# ListHDFS 2.6.0

Source: https://nifi.apache.org/docs/nifi-docs/components/org.apache.nifi/nifi-hadoop-nar/2.6.0/org.apache.nifi.processors.hadoop.ListHDFS/
Source type: Official Apache NiFi component documentation
NiFi bundle: org.apache.nifi / nifi-hadoop-nar / 2.6.0

ListHDFS

### ListHDFS

### Description:

Retrieves a listing of files from HDFS. For each file that is listed in HDFS, this processor creates a FlowFile that represents the HDFS file to be fetched in conjunction with FetchHDFS. This Processor is designed to run on Primary Node only in a cluster. If the primary node changes, the new Primary Node will pick up where the previous node left off without duplicating all of the data. Unlike GetHDFS, this Processor does not delete any data from HDFS.

Additional Details...

### Tags:

hadoop, HCFS, HDFS, get, list, ingest, source, filesystem

### Properties:

In the list below, the names of required properties appear in bold. Any other properties (not in bold) are considered optional. The table also indicates any default values, and whether a property supports the NiFi Expression Language.

 | Display Name | API Name | Default Value | Allowable Values | Description

 | Hadoop Configuration Resources | Hadoop Configuration Resources |  |  | A file or comma separated list of files which contains the Hadoop file system configuration. Without this, Hadoop will search the classpath for a 'core-site.xml' and 'hdfs-site.xml' file or will revert to a default configuration. To use swebhdfs, see 'Additional Details' section of PutHDFS's documentation.

This property expects a comma-separated list of file resources.

Supports Expression Language: true (will be evaluated using variable registry only)

 | Kerberos Credentials Service | kerberos-credentials-service |  | Controller Service API:
KerberosCredentialsService
Implementation: KeytabCredentialsService | Specifies the Kerberos Credentials Controller Service that should be used for authenticating with Kerberos

 | Kerberos User Service | kerberos-user-service |  | Controller Service API:
KerberosUserService
Implementations: KerberosPasswordUserService
KerberosKeytabUserService
KerberosTicketCacheUserService | Specifies the Kerberos User Controller Service that should be used for authenticating with Kerberos

 | Kerberos Principal | Kerberos Principal |  |  | Kerberos principal to authenticate as. Requires nifi.kerberos.krb5.file to be set in your nifi.properties
Supports Expression Language: true (will be evaluated using variable registry only)

 | Kerberos Keytab | Kerberos Keytab |  |  | Kerberos keytab associated with the principal. Requires nifi.kerberos.krb5.file to be set in your nifi.properties

This property requires exactly one file to be provided..

Supports Expression Language: true (will be evaluated using variable registry only)

 | Kerberos Password | Kerberos Password |  |  | Kerberos password associated with the principal.
Sensitive Property: true

 | Kerberos Relogin Period | Kerberos Relogin Period | 4 hours |  | Period of time which should pass before attempting a kerberos relogin. This property has been deprecated, and has no effect on processing. Relogins now occur automatically.
Supports Expression Language: true (will be evaluated using variable registry only)

 | Additional Classpath Resources | Additional Classpath Resources |  |  | A comma-separated list of paths to files and/or directories that will be added to the classpath and used for loading native libraries. When specifying a directory, all files with in the directory will be added to the classpath, but further sub-directories will not be included.

This property expects a comma-separated list of resources. Each of the resources may be of any of the following types: file, directory.

 | Directory | Directory |  |  | The HDFS directory from which files should be read
Supports Expression Language: true (will be evaluated using variable registry only)

 | Recurse Subdirectories | Recurse Subdirectories | true |
- true
- false | Indicates whether to list files from subdirectories of the HDFS directory

 | Record Writer | record-writer |  | Controller Service API:
RecordSetWriterFactory
Implementations: JsonRecordSetWriter
RecordSetWriterLookup
AvroRecordSetWriter
XMLRecordSetWriter
FreeFormTextRecordSetWriter
CSVRecordSetWriter
ParquetRecordSetWriter
ScriptedRecordSetWriter | Specifies the Record Writer to use for creating the listing. If not specified, one FlowFile will be created for each entity that is listed. If the Record Writer is specified, all entities will be written to a single FlowFile.

 | File Filter | File Filter | [^\.].* |  | Only files whose names match the given regular expression will be picked up

 | File Filter Mode | file-filter-mode | Directories and Files |
- Directories and Files
- Files Only
- Full Path  | Determines how the regular expression in File Filter will be used when retrieving listings.

 | Minimum File Age | minimum-file-age |  |  | The minimum age that a file must be in order to be pulled; any file younger than this amount of time (based on last modification date) will be ignored

 | Maximum File Age | maximum-file-age |  |  | The maximum age that a file must be in order to be pulled; any file older than this amount of time (based on last modification date) will be ignored. Minimum value is 100ms.

### Relationships:

 | Name | Description

 | success | All FlowFiles are transferred to this relationship

### Reads Attributes:
None specified.

### Writes Attributes:

 | Name | Description

 | filename | The name of the file that was read from HDFS.

 | path | The path is set to the absolute path of the file's directory on HDFS. For example, if the Directory property is set to /tmp, then files picked up from /tmp will have the path attribute set to "./". If the Recurse Subdirectories property is set to true and a file is picked up from /tmp/abc/1/2/3, then the path attribute will be set to "/tmp/abc/1/2/3".

 | hdfs.owner | The user that owns the file in HDFS

 | hdfs.group | The group that owns the file in HDFS

 | hdfs.lastModified | The timestamp of when the file in HDFS was last modified, as milliseconds since midnight Jan 1, 1970 UTC

 | hdfs.length | The number of bytes in the file in HDFS

 | hdfs.replication | The number of HDFS replicas for hte file

 | hdfs.permissions | The permissions for the file in HDFS. This is formatted as 3 characters for the owner, 3 for the group, and 3 for other users. For example rw-rw-r--

### State management:

 | Scope | Description

 | CLUSTER | After performing a listing of HDFS files, the latest timestamp of all the files listed is stored. This allows the Processor to list only files that have been added or modified after this date the next time that the Processor is run, without having to store all of the actual filenames/paths which could lead to performance problems. State is stored across the cluster so that this Processor can be run on Primary Node only and if a new Primary Node is selected, the new node can pick up where the previous node left off, without duplicating the data.

### Restricted:
This component is not restricted.

### Input requirement:
This component does not allow an incoming relationship.

### System Resource Considerations:
None specified.

### See Also:

GetHDFS, FetchHDFS, PutHDFS

## Official Additional Details

ListHDFS

### ListHDFS Filter Modes

 There are three filter modes available for ListHDFS that determine how the regular expression in the
File Filter property will be applied to listings in HDFS.
-
Directories and Files Filtering will be applied to the names of directories and files. If
Recurse Subdirectories is set to true, only subdirectories with a matching name will be searched for files that match the regular expression defined in
File Filter.
-
Files Only Filtering will only be applied to the names of files. If
Recurse Subdirectories is set to true, the entire subdirectory tree will be searched for files that match the regular expression defined in
File Filter.
-
Full Path Filtering will be applied to the full path of files. If
Recurse Subdirectories is set to true, the entire subdirectory tree will be searched for files in which the full path of the file matches the regular expression defined in
File Filter.
 Regarding
scheme and
authority, if a given file has a full path of
hdfs://hdfscluster:8020/data/txt/1.txt, the filter will evaluate the regular expression defined in
File Filter against two cases, matching if either is true:

- the full path including the scheme (
hdfs), authority (
hdfscluster:8020), and the remaining path components (
/data/txt/1.txt)
- only the path components (
/data/txt/1.txt)

### Examples:
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
