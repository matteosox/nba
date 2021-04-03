import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

export default function MyTable({
  data,
}: {
  data: Array<Array<number | string>>
}) {
  return (
    <TableContainer>
      <Table aria-label="simple table">
        <TableHead>
          <TableRow>
            {data[0].map((colName) => (
              <TableCell style={{color: 'inherit'}} key={colName}>{colName}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.slice(1).map((row, index) => (
            <TableRow key={data[0][index]}>
              {row.map((val, sub_index) => (
                <TableCell style={{color: 'inherit'}} key={sub_index}>{val}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
