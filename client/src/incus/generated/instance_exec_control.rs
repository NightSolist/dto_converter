// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceExecControl {
    pub command: String,

    pub args: HashMap<String, String>,

    pub signal: i64,

}