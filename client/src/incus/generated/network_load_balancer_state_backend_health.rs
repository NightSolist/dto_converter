// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::NetworkLoadBalancerStateBackendHealthPort;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkLoadBalancerStateBackendHealth {
    pub address: String,

    pub ports: Vec<NetworkLoadBalancerStateBackendHealthPort>,

}