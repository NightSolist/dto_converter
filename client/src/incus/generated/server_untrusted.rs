// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ServerUntrusted {
    pub apiextensions: Vec<String>,

    pub apistatus: String,

    pub apiversion: String,

    pub auth: String,

    pub public: bool,

    pub authmethods: Vec<String>,

    pub config: ConfigMap,

}