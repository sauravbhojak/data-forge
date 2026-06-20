// ── Field Types ───────────────────────────────────────────────────────────────

export const FIELD_TYPES = [
  'uuid', 'first_name', 'last_name', 'full_name', 'email', 'phone',
  'address', 'city', 'state', 'country', 'zipcode', 'latitude', 'longitude',
  'company', 'job_title', 'department', 'product_name', 'category',
  'salary', 'revenue', 'integer', 'float', 'boolean', 'date', 'datetime',
  'age', 'gender', 'username', 'password', 'url', 'ip_address', 'mac_address',
  'text', 'paragraph', 'json', 'currency', 'percentage', 'custom_string',
] as const

export type FieldType = (typeof FIELD_TYPES)[number]

export const FIELD_TYPE_LABELS: Record<FieldType, string> = {
  uuid: 'UUID',
  first_name: 'First Name',
  last_name: 'Last Name',
  full_name: 'Full Name',
  email: 'Email',
  phone: 'Phone',
  address: 'Address',
  city: 'City',
  state: 'State',
  country: 'Country',
  zipcode: 'ZIP Code',
  latitude: 'Latitude',
  longitude: 'Longitude',
  company: 'Company',
  job_title: 'Job Title',
  department: 'Department',
  product_name: 'Product Name',
  category: 'Category',
  salary: 'Salary',
  revenue: 'Revenue',
  integer: 'Integer',
  float: 'Float',
  boolean: 'Boolean',
  date: 'Date',
  datetime: 'DateTime',
  age: 'Age',
  gender: 'Gender',
  username: 'Username',
  password: 'Password',
  url: 'URL',
  ip_address: 'IP Address',
  mac_address: 'MAC Address',
  text: 'Short Text',
  paragraph: 'Paragraph',
  json: 'JSON Object',
  currency: 'Currency Code',
  percentage: 'Percentage',
  custom_string: 'Custom String',
}

export const NUMERIC_FIELD_TYPES: FieldType[] = [
  'integer', 'float', 'salary', 'revenue', 'age', 'percentage', 'latitude', 'longitude',
]

// ── Distributions ─────────────────────────────────────────────────────────────

export type Distribution =
  | 'normal'
  | 'uniform'
  | 'exponential'
  | 'skewed_left'
  | 'skewed_right'
  | 'custom'

// ── Field Definition ──────────────────────────────────────────────────────────

export interface FieldDefinition {
  name: string
  field_type: FieldType
  nullable?: boolean
  unique?: boolean
  default?: unknown
  min_value?: number | null
  max_value?: number | null
  prefix?: string | null
  suffix?: string | null
  length?: number | null
  regex?: string | null
  sequential?: boolean
  enum_values?: unknown[] | null
  description?: string | null
  distribution?: Distribution | null
}

// ── Data Quality ──────────────────────────────────────────────────────────────

export interface DataQualityConfig {
  null_rate?: number
  duplicate_rate?: number
  outlier_rate?: number
  distribution?: Distribution | null
}

// ── Table Schema ──────────────────────────────────────────────────────────────

export interface TableSchema {
  name: string
  fields: FieldDefinition[]
  row_count: number
  quality?: DataQualityConfig
}

// ── Relationships ─────────────────────────────────────────────────────────────

export type RelationshipType = 'one_to_one' | 'one_to_many' | 'many_to_one'

export interface RelationshipDefinition {
  parent_table: string
  parent_field: string
  child_table: string
  child_field: string
  relationship_type: RelationshipType
}

// ── SQL ───────────────────────────────────────────────────────────────────────

export type SQLDialect = 'postgresql' | 'mysql' | 'sqlite' | 'sqlserver'

export interface SQLSchemaRequest {
  tables: TableSchema[]
  relationships?: RelationshipDefinition[]
  dialect: SQLDialect
  include_inserts?: boolean
  sample_rows?: number
}

export interface SQLResponse {
  dialect: SQLDialect
  ddl: string
  insert_statements?: string | null
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export type AnalyticsDatasetType = 'revenue' | 'website' | 'iot' | 'vpn'

export interface AnalyticsRequest {
  dataset_type: AnalyticsDatasetType
  row_count: number
  start_date?: string | null
  trend_strength?: number
  noise_level?: number
}

// ── ERD ───────────────────────────────────────────────────────────────────────

export interface ERDRequest {
  tables: TableSchema[]
  relationships: RelationshipDefinition[]
}

export interface ERDResponse {
  mermaid: string
  table_count: number
  relationship_count: number
}

// ── API Responses ─────────────────────────────────────────────────────────────

export interface GenerationMetrics {
  row_count: number
  field_count: number
  generation_time_ms: number
  memory_delta_mb: number
}

export interface PreviewResponse {
  table_name: string
  columns: string[]
  rows: Record<string, unknown>[]
  total_count: number
  preview_count: number
  metrics: GenerationMetrics
}

export interface GenerationResponse {
  table_name: string
  row_count: number
  metrics: GenerationMetrics
  message: string
}

// ── Templates ─────────────────────────────────────────────────────────────────

export interface TemplateInfo {
  id: string
  name: string
  description: string
  icon: string
  tags: string[]
  template_type?: 'single' | 'relational'
  field_count?: number
  field_names?: string[]
  fields?: FieldDefinition[]
  table_count?: number
  relationship_count?: number
  tables?: TableSchema[]
  relationships?: RelationshipDefinition[]
}

// ── Export ───────────────────────────────────────────────────────────────────

export type ExportFormat = 'csv' | 'json' | 'sql' | 'excel'

// ── Row Counts ────────────────────────────────────────────────────────────────

export const ROW_COUNT_OPTIONS = [50, 100, 1_000, 10_000, 50_000, 100_000, 500_000, 1_000_000] as const
export type RowCountOption = (typeof ROW_COUNT_OPTIONS)[number]

export function formatRowCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(0)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`
  return String(n)
}

// ── Relational Request ────────────────────────────────────────────────────────

export interface RelationalSchemaRequest {
  tables: TableSchema[]
  relationships: RelationshipDefinition[]
}
