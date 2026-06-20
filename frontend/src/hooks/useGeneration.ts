import { useState, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '@/services/api'
import type { PreviewResponse, TableSchema } from '@/types'

export function usePreview() {
  return useMutation({
    mutationFn: (table: TableSchema) => api.preview(table),
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })
}

export function useGenerate() {
  return useMutation({
    mutationFn: (table: TableSchema) => api.generate(table),
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })
}

export function useAnalyticsPreview() {
  return useMutation({
    mutationFn: api.analyticsPreview,
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })
}

export function useGenerateERD() {
  return useMutation({
    mutationFn: api.generateERD,
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })
}

export function useGenerateSchema() {
  return useMutation({
    mutationFn: api.generateSchema,
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })
}

export function useGenerateRelations() {
  return useMutation({
    mutationFn: api.generateRelations,
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })
}
