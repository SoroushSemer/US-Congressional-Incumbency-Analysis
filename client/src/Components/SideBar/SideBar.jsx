/* 
    Written By: Soroush Semerkant
    Last Updated By: Soroush Semerkant
    Last Update Date: 02/16/2023
*/

import React, { useContext, useEffect } from 'react'
import { GlobalStoreContext } from '../../Context/store'


const SideBar = () => {
    const { store } = useContext(GlobalStoreContext);


    return (<div>
        SideBar
    </div>)
}

export default SideBar;