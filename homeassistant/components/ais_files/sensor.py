from datetime import timedelta
import glob
import logging
import os
from homeassistant.helpers.entity import Entity
from homeassistant.components.http import HomeAssistantView
from aiohttp.web import Request, Response

_LOGGER = logging.getLogger(__name__)

CONF_FOLDER_PATHS = "folder"
CONF_NAME = "name"
CONF_SORT = "sort"
DEFAULT_FILTER = "*"
DEFAULT_SORT = "date"

DOMAIN = "ais_files"

SCAN_INTERVAL = timedelta(minutes=1)


def get_files_list(folder_path, filter_term, sort):
    """Return the list of files, applying filter."""
    query = folder_path + filter_term
    """files_list = glob.glob(query)"""
    if sort == "name":
        files_list = sorted(glob.glob(query))
    elif sort == "size":
        files_list = sorted(glob.glob(query), key=os.path.getsize)
    else:
        files_list = sorted(glob.glob(query), key=os.path.getmtime)
    return files_list


def get_size(files_list):
    """Return the sum of the size in bytes of files in the list."""
    size_list = [os.stat(f).st_size for f in files_list if os.path.isfile(f)]
    return sum(size_list)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the folder sensor."""
    path = config.get(CONF_FOLDER_PATHS)
    name = config.get(CONF_NAME)

    if not hass.config.is_allowed_path(path):
        _LOGGER.error("folder %s is not valid or allowed", path)
    else:
        folder = FilesSensor(path, name, DEFAULT_FILTER, config.get(CONF_SORT))
        add_entities([folder], True)

    # aa
    hass.http.register_view(FileUpladView)


class FilesSensor(Entity):
    """Representation of a folder."""

    ICON = "mdi:folder"

    def __init__(self, folder_path, name, filter_term, sort):
        """Initialize the data object."""
        folder_path = os.path.join(folder_path, "")  # If no trailing / add it
        self._folder_path = folder_path  # Need to check its a valid path
        self._filter_term = filter_term
        self._number_of_files = None
        self._size = None
        # self._name = os.path.split(os.path.split(folder_path)[0])[1]
        self._name = name
        self._unit_of_measurement = "MB"
        self._sort = sort

    def update(self):
        """Update the sensor."""
        files_list = get_files_list(self._folder_path, self._filter_term, self._sort)
        self.fileList = files_list
        self._number_of_files = len(files_list)
        self._size = get_size(files_list)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        decimals = 2
        size_mb = round(self._size / 1e6, decimals)
        return size_mb

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self.ICON

    @property
    def device_state_attributes(self):
        """Return other details about the sensor state."""
        attr = {
            "path": self._folder_path,
            "filter": self._filter_term,
            "number_of_files": self._number_of_files,
            "bytes": self._size,
            "fileList": self.fileList,
            "sort": self._sort,
        }
        return attr

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement


class FileUpladView(HomeAssistantView):
    """A view that accepts file upload requests."""

    url = "/api/ais_file/upload"
    name = "api:ais_file:uplad"

    async def post(self, request: Request) -> Response:
        """Handle the POST request for upload file."""
        data = await request.post()
        file = data["file"]
        file_name = file.filename
        file_data = file.file.read()
        with open(
            "/data/data/pl.sviete.dom/files/home/AIS/www/img/" + file_name, "wb"
        ) as f:
            f.write(file_data)
            f.close()

        hass = request.app["hass"]
        hass.async_add_job(
            hass.services.async_call(
                "homeassistant",
                "update_entity",
                {"entity_id": "sensor.ais_gallery_img"},
            )
        )
        hass.async_add_job(
            hass.services.async_call(
                "homeassistant",
                "update_entity",
                {"entity_id": "sensor.ais_gallery_video"},
            )
        )
