# GetHDFSSequenceFile 2.6.0

Source: https://nifi.apache.org/docs/nifi-docs/components/org.apache.nifi/nifi-hadoop-nar/2.6.0/org.apache.nifi.processors.hadoop.GetHDFSSequenceFile/
Source type: Official Apache NiFi component documentation
NiFi bundle: org.apache.nifi / nifi-hadoop-nar / 2.6.0

GetHDFSSequenceFile

### GetHDFSSequenceFile

### Description:

Fetch sequence files from Hadoop Distributed File System (HDFS) into FlowFiles

### Tags:

hadoop, HCFS, HDFS, get, fetch, ingest, source, sequence file

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
- false | Indicates whether to pull files from subdirectories of the HDFS directory

 | Keep Source File | Keep Source File | false |
- true
- false | Determines whether to delete the file from HDFS after it has been successfully transferred. If true, the file will be fetched repeatedly. This is intended for testing only.

 | File Filter Regex | File Filter Regex |  |  | A Java Regular Expression for filtering Filenames; if a filter is supplied then only files whose names match that Regular Expression will be fetched, otherwise all files will be fetched

 | Filter Match Name Only | Filter Match Name Only | true |
- true
- false | If true then File Filter Regex will match on just the filename, otherwise subdirectory names will be included with filename in the regex comparison

 | Ignore Dotted Files | Ignore Dotted Files | true |
- true
- false | If true, files whose names begin with a dot (".") will be ignored

 | Minimum File Age | Minimum File Age | 0 sec |  | The minimum age that a file must be in order to be pulled; any file younger than this amount of time (based on last modification date) will be ignored

 | Maximum File Age | Maximum File Age |  |  | The maximum age that a file must be in order to be pulled; any file older than this amount of time (based on last modification date) will be ignored

 | Polling Interval | Polling Interval | 0 sec |  | Indicates how long to wait between performing directory listings

 | Batch Size | Batch Size | 100 |  | The maximum number of files to pull in each iteration, based on run schedule.

 | IO Buffer Size | IO Buffer Size |  |  | Amount of memory to use to buffer file contents during IO. This overrides the Hadoop Configuration

 | Compression codec | Compression codec | NONE |
- NONE
- DEFAULT
- BZIP
- GZIP
- LZ4
- LZO
- SNAPPY
- AUTOMATIC  | No Description Provided.

 | FlowFile Content | FlowFile Content | VALUE ONLY |
- VALUE ONLY
- KEY VALUE PAIR | Indicate if the content is to be both the key and value of the Sequence File, or just the value.

### Relationships:

 | Name | Description

 | success | All files retrieved from HDFS are transferred to this relationship

### Reads Attributes:
None specified.

### Writes Attributes:

 | Name | Description

 | filename | The name of the file that was read from HDFS.

 | path | The path is set to the relative path of the file's directory on HDFS. For example, if the Directory property is set to /tmp, then files picked up from /tmp will have the path attribute set to "./". If the Recurse Subdirectories property is set to true and a file is picked up from /tmp/abc/1/2/3, then the path attribute will be set to "abc/1/2/3".

### State management:
This component does not store state.

### Restricted:

 | Required Permission | Explanation

 | read distributed filesystem | Provides operator the ability to retrieve any file that NiFi has access to in HDFS or the local filesystem.

 | write distributed filesystem | Provides operator the ability to delete any file that NiFi has access to in HDFS or the local filesystem.

### Input requirement:
This component does not allow an incoming relationship.

### System Resource Considerations:
None specified.

### See Also:

PutHDFS
