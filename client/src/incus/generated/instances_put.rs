// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::InstanceStatePut;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstancesPut {
    pub state: Option<InstanceStatePut>,

}