# PutHDFS 2.6.0

Source: https://nifi.apache.org/docs/nifi-docs/components/org.apache.nifi/nifi-hadoop-nar/2.6.0/org.apache.nifi.processors.hadoop.PutHDFS/
Source type: Official Apache NiFi component documentation
NiFi bundle: org.apache.nifi / nifi-hadoop-nar / 2.6.0

PutHDFS

### PutHDFS

### Description:

Write FlowFile data to Hadoop Distributed File System (HDFS)

Additional Details...

### Tags:

hadoop, HCFS, HDFS, put, copy, filesystem

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

 | Directory | Directory |  |  | The parent HDFS directory to which files should be written. The directory will be created if it doesn't exist.
Supports Expression Language: true (will be evaluated using flow file attributes and variable registry)

 | Conflict Resolution Strategy | Conflict Resolution Strategy | fail |
- replace
- ignore
- fail
- append  | Indicates what should happen when a file with the same name already exists in the output directory

 | Append Mode | Append Mode | DEFAULT |
- DEFAULT
- AVRO | Defines the append strategy to use when the Conflict Resolution Strategy is set to 'append'.

This Property is only considered if the [Conflict Resolution Strategy] Property has a value of "append".

 | Writing Strategy | writing-strategy | Write and rename |
- Write and rename
- Simple write  | Defines the approach for writing the FlowFile data.

 | Block Size | Block Size |  |  | Size of each block as written to HDFS. This overrides the Hadoop Configuration

 | IO Buffer Size | IO Buffer Size |  |  | Amount of memory to use to buffer file contents during IO. This overrides the Hadoop Configuration

 | Replication | Replication |  |  | Number of times that HDFS will replicate each file. This overrides the Hadoop Configuration

 | Permissions umask | Permissions umask |  |  | A umask represented as an octal number which determines the permissions of files written to HDFS. This overrides the Hadoop property "fs.permissions.umask-mode". If this property and "fs.permissions.umask-mode" are undefined, the Hadoop default "022" will be used. If the PutHDFS target folder has a default ACL defined, the umask property is ignored by HDFS.

 | Remote Owner | Remote Owner |  |  | Changes the owner of the HDFS file to this value after it is written. This only works if NiFi is running as a user that has HDFS super user privilege to change owner
Supports Expression Language: true (will be evaluated using flow file attributes and variable registry)

 | Remote Group | Remote Group |  |  | Changes the group of the HDFS file to this value after it is written. This only works if NiFi is running as a user that has HDFS super user privilege to change group
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

 | Ignore Locality | Ignore Locality | false |
- true
- false | Directs the HDFS system to ignore locality rules so that data is distributed randomly throughout the cluster

### Relationships:

 | Name | Description

 | success | Files that have been successfully written to HDFS are transferred to this relationship

 | failure | Files that could not be written to HDFS for some reason are transferred to this relationship

### Reads Attributes:

 | Name | Description

 | filename | The name of the file written to HDFS comes from the value of this attribute.

### Writes Attributes:

 | Name | Description

 | filename | The name of the file written to HDFS is stored in this attribute.

 | absolute.hdfs.path | The absolute path to the file on HDFS is stored in this attribute.

 | hadoop.file.url | The hadoop url for the file is stored in this attribute.

 | target.dir.created | The result(true/false) indicates if the folder is created by the processor.

### State management:
This component does not store state.

### Restricted:

 | Required Permission | Explanation

 | write distributed filesystem | Provides operator the ability to delete any file that NiFi has access to in HDFS or the local filesystem.

### Input requirement:
This component requires an incoming relationship.

### System Resource Considerations:
None specified.

### See Also:

GetHDFS

## Official Additional Details

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
