use std::collections::HashMap;

// Newtype Pattern untuk Identifier agar lebih rapi
#[derive(Debug, Clone)]
pub struct Identifier(pub String);

#[derive(Debug, Clone)]
pub enum Module {
    Program(Vec<TopStatement>),
}

#[derive(Debug, Clone)]
pub enum TopStatement {
    Block(Vec<Statement>),
    NonBlock(Statement),
}

#[derive(Debug, Clone)]
pub enum Statement {
    VarsDecl(VariablesDeclare),
    Expr(Expression),
}

#[derive(Debug, Clone)]
pub enum VariablesDeclare {
    VarDecl(VariableDecl),
    FinalDecl(FinalDecl),
}

#[derive(Debug, Clone)]
pub struct VariableDecl {
    pub name: Identifier,
    pub type_ann: Identifier,
    pub value: Expression,
}

#[derive(Debug, Clone)]
pub struct FinalDecl {
    pub name: Identifier,
    pub type_ann: Identifier,
    pub value: Expression,
}

#[derive(Debug, Clone)]
pub enum Expression {
    Term(Terminal),
}

#[derive(Debug, Clone)]
pub struct Terminal {
    pub prefix: Prefix,
    pub postfix: Vec<Postfix>,
}

#[derive(Debug, Clone)]
pub enum Prefix {
    Literal(Literal),
    Id(Identifier),
    Expr(Box<Expression>), 
}

#[derive(Debug, Clone)]
pub enum Postfix {
    Attr(Identifier),
    Index(Vec<Expression>)
}

#[derive(Debug, Clone)]
pub enum Literal {
    Teks(String),
    Angka(i64),
    Desimal(f64),
    Boolean(bool),
    Null,
    // Tambahkan ini untuk Array dan Dictionary
    Daftar(Vec<Expression>),
    Kamus(HashMap<String, Expression>),
}

pub fn _default_value(type_ann: &Identifier) -> Expression {
    let name = &type_ann.0; // Mengambil string dari Identifier(String)
    
    let literal = if name == "angka" {
        Literal::Angka(0)
    } else if name == "teks" {
        Literal::Teks("".to_string())
    } else if name == "boolean" {
        Literal::Boolean(false)
    } else if name == "desimal" {
        Literal::Desimal(0.0)
    } else {
        Literal::Null // Default untuk tipe lainnya
    };

    // Bungkus Literal ke dalam hirarki Expression Anda
    Expression::Term(Terminal {
        prefix: Prefix::Literal(literal),
        postfix: vec![],
    })
}