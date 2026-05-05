// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ClusterMemberConfigKey;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Cluster {
    pub servername: String,

    pub enabled: bool,

    pub memberconfig: Vec<ClusterMemberConfigKey>,

}