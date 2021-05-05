import Table from '@material-ui/core/Table'
import TableBody from '@material-ui/core/TableBody'
import TableCell from '@material-ui/core/TableCell'
import TableContainer from '@material-ui/core/TableContainer'
import TableHead from '@material-ui/core/TableHead'
import TableRow from '@material-ui/core/TableRow'
import styles from './table.module.css'

export default function MyTable({
  data,
}: {
  data: Array<Array<number | string>>
}) {
  return (
    <TableContainer className={styles.table}>
      <Table size="small" aria-label="simple table">
        <TableHead>
          <TableRow>
            {data[0].map((colName, index) => (
              <TableCell className={index === 0 ? styles.firstHeaderCell : styles.headerCell} key={colName}>{colName}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.slice(1).map((row, index) => (
            <TableRow key={data[0][index]}>
              {row.map((val, sub_index) => (
                <TableCell className={sub_index === 0 ? styles.firstBodyCell : styles.tableCell} key={sub_index}>{val}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
