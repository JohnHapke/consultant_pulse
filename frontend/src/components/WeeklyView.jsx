import { SituationBlock } from './SituationBlock'
import { RAGGrid } from './RAGGrid'
import { WorkloadChart } from './WorkloadChart'
import { buildLookup, computeRagChanges } from '../utils/delta'

export function WeeklyView({ data, prevData }) {
  const prevLookup = prevData ? buildLookup(prevData.consultants) : null
  const ragChanges = computeRagChanges(data.consultants, prevLookup)

  return (
    <div>
      <SituationBlock
        aggregated={data.aggregated}
        nameMap={data.name_map}
        blockers={data.blockers}
        callsRequested={data.calls_requested}
        missingConsultants={data.missing}
        isMonthly={false}
        ragChanges={ragChanges}
        consultants={data.consultants}
      />
      <RAGGrid consultants={data.consultants} prevLookup={prevLookup} />
      <WorkloadChart consultants={data.consultants} prevLookup={prevLookup} />
    </div>
  )
}
