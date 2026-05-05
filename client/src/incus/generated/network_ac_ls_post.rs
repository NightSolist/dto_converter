// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::NetworkACLRule;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkACLsPost {
    pub name: String,

    pub description: String,

    pub egress: Vec<NetworkACLRule>,

    pub ingress: Vec<NetworkACLRule>,

    pub config: ConfigMap,

}