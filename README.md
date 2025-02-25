# Synaptics Astra AI examples

In the following tutorials, we will run NPU-accelerated AI inference on Synaptics Astra using the `SynapRT` Python package.

![python](/img/python-logo-generic.svg)

We will install SynapRT examples on our board and run through them in the following tutorial sections.

In the Astra console window, type (or copy paste) the following to download the examples to your board:

<InstallGuide item="examples" />

We're going to use a Python virtual environment to keep any packages we install separate in order to avoid any version conflicts. This takes under a minute:

```bash
python3 -m venv .venv --system-site-packages
```

:::info
Specifying `--system-site-packages` means it copies across prebuilt Python packages on the Astra firmware image. 
:::

The we'll activate the virtual environment, which means any python packages we install will be kept in the local `.venv` directory:

```
source .venv/bin/activate
```

Your prompt should new look like: 

<pre>
(.venv) root@sl1680:~/ew2025-workshop#
</pre>

Next, let's install the Python package dependencies:

<InstallGuide item="synap-python" />

**Congraulations! You now have the tutorial examples installed on your Astra board.**



:::note
For the Embedded World workshop, we are hosting all workshop materials on a local server to ensure no connectivity issues.

However, the Python package will be publicly available and simpler to install using `pip` in real-world development scenario.
:::








