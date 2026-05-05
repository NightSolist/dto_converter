// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkLoadBalancerStateBackendHealthPort {
    pub protocol: String,

    pub port: i64,

    pub status: String,

}