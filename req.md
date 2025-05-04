IPAM to manage the CIDRs in below types
Type of CIDRs
- Engineers used to allocate the CIDRs for each typical cases. We save it in some file. We call it Static_CIDR
- Two type of cidr in AWS
    - CIRDs allocated to VPC (VPC_CIDR)
    - Subnet owned CIDR (Subnet_CIDR), which is allocated from VPC_CIDR 
    - VPC_CIDR normally is the CIDRs in Static_CIDR
- EIP is individual public IP address in AWS. We treat it as /32 CIDRs

Req: (User case diagrams)
- Load CIDR from static file and query from AWS
    - Admin load Static_CIDR 
    - Admin load AWS VPC_CIDR and Subnet_CIDR
- Query CIDR or tag. (Each CIDR is with tags).
    - User ask tag for certain CIDR
    - User query the CIDR list which contains the given tags
- Find available CIDR
    - User ask to list all the child CIDRs of the given CIDR. (Not include grandchild CIDR. e.g. IPAM only contains three CIDRs 10.0.0.0/8, 10.0.0.0/16,   10.0.0.0/20 .  10.0.0.0/8 is parent CIDR, 10.0.0.0/16 is its child CIDR, and 10.0.0.0/20 is grandchild CIDR of 10.0.0.0/8 and child CIDR of 10.0.0.0/16)
    - User request a CIDR with certain mask length under given CIDR.

