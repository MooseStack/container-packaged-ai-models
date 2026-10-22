{{- define "model.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "model.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "model.labels" -}}
app: {{ include "model.fullname" . }}
app.kubernetes.io/name: {{ include "model.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "model.selectorLabels" -}}
app: {{ include "model.fullname" . }}
{{- end }}
