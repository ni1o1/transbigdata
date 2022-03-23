"""
`TransBigData`: A Python package develop for transportation spatio-temporal big
data processing, analysis and visualization.
"""

from .plot_map import (
    plot_map,
    plotscale,
    set_mapboxtoken,
    set_imgsavepath
)
from .CoordinatesConverter import (
    gcj02tobd09,
    bd09togcj02,
    wgs84togcj02,
    gcj02towgs84,
    wgs84tobd09,
    bd09towgs84,
    bd09mctobd09,
    getdistance,
    transform_shape
)
from .grids import (
    rect_grids,
    grid_params,
    GPS_to_grids,
    grids_centre,
    gridid_to_polygon,
    hexagon_grids,
    gridid_sjoin_shape,
    grid_params_optimize,
    regenerate_params,
    geohash_encode,
    geohash_decode,
    geohash_togrid
)
from .gisprocess import (
    ckdnearest,
    ckdnearest_point,
    ckdnearest_line,
    splitline_with_length,
    merge_polygon,
    polyon_exterior,
    ellipse_params,
    ellipse_plot
)
from .odprocess import (
    odagg_grid,
    odagg_shape,
    tolinewitharrow
)
from .preprocess import (
    clean_same,
    clean_drift,
    clean_outofbounds,
    clean_outofshape,
    clean_traj,
    dataagg,
    id_reindex_disgap,
    id_reindex
)
from .bikedata import (
    bikedata_to_od
)
from .taxigps import (
    clean_taxi_status,
    taxigps_to_od,
    taxigps_traj_point
)
from .traj import (
    plot_activity,
    traj_stay_move,
    traj_densify,
    traj_sparsify,
    points_to_traj,
    dumpjson
)
from .quality import (
    sample_duration,
    data_summary
)
from .busgps import (
    busgps_arriveinfo,
    busgps_onewaytime
)
from .getbusdata import (
    getadmin,
    getbusdata,
    get_isochrone_amap,
    get_isochrone_mapbox,
    split_subwayline,
    metro_network
)
from .visualization import (
    visualization_trip,
    visualization_od,
    visualization_data
)


name = "transbigdata"
__version__ = '0.3.11'
__author__ = 'Qing Yu <qingyu0815@foxmail.com>'
