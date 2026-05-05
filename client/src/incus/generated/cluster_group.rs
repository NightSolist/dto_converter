// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ClusterGroup {
    pub usedby: Vec<String>,

    pub description: String,

    pub members: Vec<String>,

    pub config: ConfigMap,

    pub name: String,

}