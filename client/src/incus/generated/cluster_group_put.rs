// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ClusterGroupPut {
    pub description: String,

    pub members: Vec<String>,

    pub config: ConfigMap,

}