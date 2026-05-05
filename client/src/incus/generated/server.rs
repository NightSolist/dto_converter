// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::ServerEnvironment;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Server {
    pub authusername: String,

    pub authusermethod: String,

    pub environment: ServerEnvironment,

    pub apiextensions: Vec<String>,

    pub apistatus: String,

    pub apiversion: String,

    pub auth: String,

    pub public: bool,

    pub authmethods: Vec<String>,

    pub config: ConfigMap,

}