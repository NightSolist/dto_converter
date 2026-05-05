// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ClusterMember {
    pub servername: String,

    pub url: String,

    pub database: bool,

    pub status: String,

    pub message: String,

    pub architecture: String,

    pub roles: Vec<String>,

    pub failuredomain: String,

    pub description: String,

    pub config: ConfigMap,

    pub groups: Vec<String>,

}