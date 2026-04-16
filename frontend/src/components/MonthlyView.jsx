import { SituationBlock } from './SituationBlock'
import { RAGGrid } from './RAGGrid'
import { WorkloadChart } from './WorkloadChart'
import { MonthlyScores } from './MonthlyScores'
import { ConsultantCards } from './ConsultantCards'
import { mergeConsultants } from '../utils/mergeConsultants'
import { buildLookup, computeRagChanges } from '../utils/delta'

export function MonthlyView({ data, prevData }) {
  const merged = mergeConsultants(data.consultants, data.lead_reports)
  const prevLookup = prevData ? buildLookup(prevData.consultants) : null
  const prevMergedLookup = prevData
    ? buildLookup(mergeConsultants(prevData.consultants, prevData.lead_reports))
    : null
  const ragChanges = computeRagChanges(data.consultants, prevLookup)

  return (
    <div>
      <SituationBlock
        aggregated={data.aggregated}
        nameMap={data.name_map}
        risks={data.risks}
        missingConsultants={data.missing_consultants}
        missingLeads={data.missing_leads}
        isMonthly={true}
        ragChanges={ragChanges}
      />
      <RAGGrid consultants={data.consultants} prevLookup={prevLookup} />
      <MonthlyScores aggregated={data.aggregated} prevAggregated={prevData?.aggregated} />
      <WorkloadChart consultants={data.consultants} prevLookup={prevLookup} />
      <ConsultantCards consultants={merged} prevLookup={prevMergedLookup} />
    </div>
  )
}
