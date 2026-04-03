use std::collections::HashMap;

/*
 * Public Enum
 */

#[derive(Debug, Clone)]
pub enum Value {
    Teks(String),
    Angka(i64),
    Desimal(f64),
    Boolean(bool),
    Daftar(Vec<Value>),
    Kamus(HashMap<String, Value>),
    Null,
}

#[derive(Debug, Clone)]
pub struct Variable {
    pub tipe: String,
    pub value: Value,
    pub address: String,
    pub constant: bool,
}

/*
 * implement for Value
 */

impl From<String> for Value {
    fn from(v: String) -> Self { Value::Teks(v) }
}

impl From<&str> for Value {
    fn from(v: &str) -> Self { Value::Teks(v.to_string()) }
}

impl From<i64> for Value {
    fn from(v: i64) -> Self { Value::Angka(v) }
}

impl From<bool> for Value {
    fn from(v: bool) -> Self { Value::Boolean(v) }
}

pub fn get_value<T: Into<Value>>(val: T) -> Value {
    val.into()
}