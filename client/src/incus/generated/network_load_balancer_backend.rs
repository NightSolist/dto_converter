// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkLoadBalancerBackend {
    pub name: String,

    pub description: String,

    pub targetport: String,

    pub targetaddress: String,

}