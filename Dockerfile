FROM reg.weizom.com/wzbase/python27:1.0

MAINTAINER gaia-team

RUN pip install -U \
   git+https://git2.weizzz.com:84/microservice/eaglet.git \
   git+https://git2.weizzz.com:84/microservice/mns_python_sdk.git \
   git+https://git2.weizzz.com:84/microservice/servicecli.git \
   && rm -rf ~/.pip ~/.cache
  ADD . /service
  WORKDIR /service
ENTRYPOINT ["/usr/local/bin/dumb-init", "/bin/bash", "start_service.sh"]
