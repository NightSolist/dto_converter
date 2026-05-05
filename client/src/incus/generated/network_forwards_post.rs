// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::NetworkForwardPort;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkForwardsPost {
    pub listenaddress: String,

    pub description: String,

    pub config: ConfigMap,

    pub ports: Vec<NetworkForwardPort>,

}