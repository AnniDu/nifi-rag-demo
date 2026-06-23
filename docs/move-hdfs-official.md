# MoveHDFS 2.6.0

Source: https://nifi.apache.org/docs/nifi-docs/components/org.apache.nifi/nifi-hadoop-nar/2.6.0/org.apache.nifi.processors.hadoop.MoveHDFS/
Source type: Official Apache NiFi component documentation
NiFi bundle: org.apache.nifi / nifi-hadoop-nar / 2.6.0

MoveHDFS

### MoveHDFS

### Description:

Rename existing files or a directory of files (non-recursive) on Hadoop Distributed File System (HDFS).

### Tags:

hadoop, HCFS, HDFS, put, move, filesystem, moveHDFS

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

 | Conflict Resolution Strategy | Conflict Resolution Strategy | fail |
- replace
- ignore
- fail  | Indicates what should happen when a file with the same name already exists in the output directory

 | Input Directory or File | Input Directory or File | ${path} |  | The HDFS directory from which files should be read, or a single file to read.
Supports Expression Language: true (will be evaluated using flow file attributes and variable registry)

 | Output Directory | Output Directory |  |  | The HDFS directory where the files will be moved to
Supports Expression Language: true (will be evaluated using flow file attributes and variable registry)

 | HDFS Operation | HDFS Operation | move |
- move
- copy | The operation that will be performed on the source file

 | File Filter Regex | File Filter Regex |  |  | A Java Regular Expression for filtering Filenames; if a filter is supplied then only files whose names match that Regular Expression will be fetched, otherwise all files will be fetched

 | Ignore Dotted Files | Ignore Dotted Files | true |
- true
- false | If true, files whose names begin with a dot (".") will be ignored

 | Remote Owner | Remote Owner |  |  | Changes the owner of the HDFS file to this value after it is written. This only works if NiFi is running as a user that has HDFS super user privilege to change owner

 | Remote Group | Remote Group |  |  | Changes the group of the HDFS file to this value after it is written. This only works if NiFi is running as a user that has HDFS super user privilege to change group

### Relationships:

 | Name | Description

 | success | Files that have been successfully renamed on HDFS are transferred to this relationship

 | failure | Files that could not be renamed on HDFS are transferred to this relationship

### Reads Attributes:

 | Name | Description

 | filename | The name of the file written to HDFS comes from the value of this attribute.

### Writes Attributes:

 | Name | Description

 | filename | The name of the file written to HDFS is stored in this attribute.

 | absolute.hdfs.path | The absolute path to the file on HDFS is stored in this attribute.

 | hadoop.file.url | The hadoop url for the file is stored in this attribute.

### State management:
This component does not store state.

### Restricted:

 | Required Permission | Explanation

 | read distributed filesystem | Provides operator the ability to retrieve any file that NiFi has access to in HDFS or the local filesystem.

 | write distributed filesystem | Provides operator the ability to delete any file that NiFi has access to in HDFS or the local filesystem.

### Input requirement:
This component allows an incoming relationship.

### System Resource Considerations:
None specified.

### See Also:

PutHDFS, GetHDFS
