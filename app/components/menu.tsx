import React from 'react'
import Link from 'next/link'
import Button from '@material-ui/core/Button'
import MenuList from '@material-ui/core/MenuList'
import MenuItem from '@material-ui/core/MenuItem'
import Popper from '@material-ui/core/Popper'
import Paper from '@material-ui/core/Paper'

export default function HoverMenu({
  name,
  items,
  className
}: {
  name: string,
  items: {name: string, link: string}[],
  className?: string
}) {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null)
  const [buttonHover, setButtonHover] = React.useState<boolean>(false)
  const [menuHover, setMenuHover] = React.useState<boolean>(false)
  const handleButtonHover = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
    setButtonHover(true)
  }
  const handleButtonNoHover = () => {
    setButtonHover(false)
  }
  const handleMenuHover = () => {
    setMenuHover(true)
  }
  const handleMenuNoHover = () => {
    setMenuHover(false)
  }

  return (
    <div>
      <Button className={className} style={{cursor: 'default'}} variant="outlined" aria-controls="simple-menu" aria-haspopup="true" onMouseEnter={handleButtonHover} onMouseLeave={handleButtonNoHover}>
        {name}
      </Button>
      <Popper
        open={buttonHover || menuHover}
        anchorEl={anchorEl}
        keepMounted
        style={{zIndex: 1101}}
      >
        <Paper
          onMouseEnter={handleMenuHover}
          onMouseLeave={handleMenuNoHover}
          style={{maxHeight: '50vh', overflow: 'auto'}}
        >
          <MenuList id="simple-menu">
            {items.map(({name, link}) => (
              <MenuItem key={name}>
                <Link href={link}>
                  <a>{name}</a>
                </Link>
              </MenuItem>
            ))}
          </MenuList>
        </Paper>
      </Popper>
    </div>
  )
}
