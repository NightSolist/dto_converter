// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkForwardPort {
    pub description: String,

    pub protocol: String,

    pub listenport: String,

    pub targetport: String,

    pub targetaddress: String,

    pub snat: bool,

}