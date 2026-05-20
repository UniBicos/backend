export type StatusPedido =
  | 'CRIADO'
  | 'ACEITO_PELO_VENDEDOR'
  | 'EM_PREPARO'
  | 'ENTREGA_ACEITA'
  | 'SAIU_PARA_ENTREGA'
  | 'ENTREGUE'
  | 'CANCELADO'

export type TiposPerfil = 'ENTREGADOR' | 'LOJA'

export type StatusPagamento = 'AGUARDANDO_PAGAMENTO' | 'PAGO' | 'CONFIRMADO' | 'CANCELADO'

export interface BaseModel {
  id_user_cad?: number | null
  dt_cad: string
  id_user_alt?: number | null
  dt_alt: string
}

export interface Usuario extends BaseModel {
  id: number
  email: string
  nome: string
  id_instituicao?: number | null
  cpf?: string | null
  cnpj?: string | null
  telefone: string
  matricula?: string | null
}

export interface InstituicoesEnsino extends BaseModel {
  id_instituicao: number
  nome: string
  sigla: string
  campus: string
  cidade: string
  estado: string
}

export interface EmailsInstituicao extends BaseModel {
  id_email_instituicao: number
  id_instituicao: number
  email: string
}

export interface Movimentacoes extends BaseModel {
  id_movimentacoes: number
  id_usuario: number
  tipo_perfil: TiposPerfil
  valor: number
}

export interface Compradores extends BaseModel {
  id_comprador: number
  id_usuario: number
}

export interface Lojas extends BaseModel {
  id_loja: number
  id_usuario: number
  nome_fantasia: string
  aberto: boolean
  departamento?: string | null
  localizacao: string
  avaliacao: number
  saldo_disponivel: number
}

export interface Entregadores extends BaseModel {
  id_entregador: number
  id_usuario: number
  aberto: boolean
  saldo_disponivel: number
  avaliacao: number
}

export interface Categorias extends BaseModel {
  id_categoria: number
  nome_categoria: string
  icon: string
}

export interface Produtos extends BaseModel {
  id_produto: number
  id_loja: number
  id_categoria: number
  nome: string
  imagem: string
  descricao: string
  preco: number
  disponivel: boolean
}

export interface Pedidos extends BaseModel {
  id_pedido: number
  id_cliente: number
  id_loja: number
  id_entregador?: number | null
  taxa_entrega: number
  total_pedido: number
  status_pedido: StatusPedido
  token: string
  sala_entrega?: string | null
  bloco_entrega?: string | null
  descricao_local?: string | null
}

export interface PedidoProdutos extends BaseModel {
  id_pedido_produto: number
  id_pedido: number
  id_produto: number
  quantidade: number
  preco_un: number
}

export interface Pagamento extends BaseModel {
  id_pagamento: number
  id_pedido: number
  id_intent: string
  status_pagamento: StatusPagamento
}
