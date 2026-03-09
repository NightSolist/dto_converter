// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceStatePut {
    pub action: String,

    pub timeout: i64,

    pub force: bool,

    pub stateful: bool,

}