import uvicorn
from main import app

from ggt.lib.utils import (
    get_config_val as cfg
)


if __name__ == '__main__':
    uvicorn.run(
        app,
        host=cfg('server.host'),
        port=cfg('server.sms_queue_processor_port'),
        debug=cfg('log_level')
    )
