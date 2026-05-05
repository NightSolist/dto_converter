// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::NetworkLoadBalancerBackend;
use crate::incus::NetworkLoadBalancerPort;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkLoadBalancer {
    pub listenaddress: String,

    pub location: String,

    pub description: String,

    pub config: ConfigMap,

    pub backends: Vec<NetworkLoadBalancerBackend>,

    pub ports: Vec<NetworkLoadBalancerPort>,

}