# FetchHDFS 2.6.0

Source: https://nifi.apache.org/docs/nifi-docs/components/org.apache.nifi/nifi-hadoop-nar/2.6.0/org.apache.nifi.processors.hadoop.FetchHDFS/
Source type: Official Apache NiFi component documentation
NiFi bundle: org.apache.nifi / nifi-hadoop-nar / 2.6.0

FetchHDFS

### FetchHDFS

### Description:

Retrieves a file from HDFS. The content of the incoming FlowFile is replaced by the content of the file in HDFS. The file in HDFS is left intact without any changes being made to it.

### Tags:

hadoop, hcfs, hdfs, get, ingest, fetch, source

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

 | HDFS Filename | HDFS Filename | ${path}/${filename} |  | The name of the HDFS file to retrieve
Supports Expression Language: true (will be evaluated using flow file attributes and variable registry)

 | Compression codec | Compression codec | NONE |
- NONE
- DEFAULT
- BZIP
- GZIP
- LZ4
- LZO
- SNAPPY
- AUTOMATIC  | No Description Provided.

### Relationships:

 | Name | Description

 | success | FlowFiles will be routed to this relationship once they have been updated with the content of the HDFS file

 | comms.failure | FlowFiles will be routed to this relationship if the content of the HDFS file cannot be retrieve due to a communications failure. This generally indicates that the Fetch should be tried again.

 | failure | FlowFiles will be routed to this relationship if the content of the HDFS file cannot be retrieved and trying again will likely not be helpful. This would occur, for instance, if the file is not found or if there is a permissions issue

### Reads Attributes:
None specified.

### Writes Attributes:

 | Name | Description

 | hdfs.failure.reason | When a FlowFile is routed to 'failure', this attribute is added indicating why the file could not be fetched from HDFS

 | hadoop.file.url | The hadoop url for the file is stored in this attribute.

### State management:
This component does not store state.

### Restricted:

 | Required Permission | Explanation

 | read distributed filesystem | Provides operator the ability to retrieve any file that NiFi has access to in HDFS or the local filesystem.

### Input requirement:
This component requires an incoming relationship.

### System Resource Considerations:
None specified.

### See Also:

ListHDFS, GetHDFS, PutHDFS
