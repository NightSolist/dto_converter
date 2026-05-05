// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkLoadBalancerPort {
    pub description: String,

    pub protocol: String,

    pub listenport: String,

    pub targetbackend: Vec<String>,

}