// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ClusterMemberConfigKey;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InitClusterPreseed {
    pub clustercertificatepath: String,

    pub clusteraddress: String,

    pub clustercertificate: String,

    pub serveraddress: String,

    pub clustertoken: String,

    pub servername: String,

    pub enabled: bool,

    pub memberconfig: Vec<ClusterMemberConfigKey>,

}